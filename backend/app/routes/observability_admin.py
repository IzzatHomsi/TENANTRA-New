from typing import Optional, Dict, Any
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
import os
import threading
import time

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.app_setting import AppSetting
from app.models.user import User
from app.observability.metrics import record_grafana_health, record_grafana_misconfig

router = APIRouter(prefix="/admin/observability", tags=["Admin Observability"])
logger = logging.getLogger(__name__)


def _get_setting(db: Session, key: str) -> Optional[str]:
    row = db.query(AppSetting).filter(AppSetting.tenant_id.is_(None), AppSetting.key == key).first()
    return (row.value if row else None) or None


HEALTH_MIN_INTERVAL = int(os.getenv("GRAFANA_HEALTH_MIN_INTERVAL", "30"))
HEALTH_FAILURE_THRESHOLD = int(os.getenv("GRAFANA_HEALTH_FAILURE_THRESHOLD", "3"))
HEALTH_CIRCUIT_TIMEOUT = int(os.getenv("GRAFANA_HEALTH_CIRCUIT_TIMEOUT", "120"))


class _HealthState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.last_payload: Optional[Dict[str, Any]] = None
        self.last_checked: float = 0.0
        self.failure_count: int = 0
        self.circuit_open_until: float = 0.0

    def should_short_circuit(self) -> bool:
        return time.time() < self.circuit_open_until

    def record_result(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        success = bool(payload.get("ok"))
        payload["cached"] = False
        with self.lock:
            self.last_payload = payload
            self.last_checked = payload.get("checked_at", time.time())
            if success:
                self.failure_count = 0
                self.circuit_open_until = 0.0
            else:
                self.failure_count += 1
                if self.failure_count >= HEALTH_FAILURE_THRESHOLD:
                    self.circuit_open_until = self.last_checked + max(HEALTH_CIRCUIT_TIMEOUT, 30)
        record_grafana_health(success)
        return payload

    def cached(self, reason: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            if not self.last_payload:
                return None
            cached = dict(self.last_payload)
            cached["cached"] = True
            cached["cache_reason"] = reason
            return cached

    def should_throttle(self) -> bool:
        with self.lock:
            if not self.last_payload:
                return False
            return (time.time() - self.last_checked) < max(HEALTH_MIN_INTERVAL, 5)

    def mark_attempt(self) -> None:
        with self.lock:
            self.last_checked = time.time()


_GRAFANA_HEALTH_STATE = _HealthState()


@router.get("/grafana/health", response_model=dict)
def grafana_health(db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = _get_setting(db, 'grafana.url')
    if not base:
        record_grafana_health(False)
        record_grafana_misconfig()
        logger.warning("Grafana health check aborted: grafana.url app setting not configured")
        cached = _GRAFANA_HEALTH_STATE.cached("missing-config")
        if cached:
            cached["configured"] = False
            cached.setdefault("ok", False)
            cached.setdefault("message", "grafana.url not configured")
            cached.setdefault("detail", "grafana.url not configured")
            return cached
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"message": "grafana.url not configured", "configured": False},
        )
    if _GRAFANA_HEALTH_STATE.should_short_circuit():
        cached = _GRAFANA_HEALTH_STATE.cached("circuit-open")
        if cached:
            return cached
        raise HTTPException(status_code=503, detail="Grafana health check circuit is open; retry later.")
    if _GRAFANA_HEALTH_STATE.should_throttle():
        cached = _GRAFANA_HEALTH_STATE.cached("throttled")
        if cached:
            return cached
    url = f"{base.rstrip('/')}/api/health"
    start = time.perf_counter()
    try:
        _GRAFANA_HEALTH_STATE.mark_attempt()
        r = requests.get(url, timeout=5)
        payload = {
            "url": url,
            "status": r.status_code,
            "ok": r.ok,
            "body": (r.text[:200] if r.text else None),
            "checked_at": time.time(),
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
        return _GRAFANA_HEALTH_STATE.record_result(payload)
    except Exception as e:
        payload = {
            "url": url,
            "status": 502,
            "ok": False,
            "error": str(e),
            "checked_at": time.time(),
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
        _GRAFANA_HEALTH_STATE.record_result(payload)
        cached = _GRAFANA_HEALTH_STATE.cached("exception")
        if cached:
            return cached
        raise HTTPException(status_code=502, detail=str(e))


def _auth_headers() -> dict:
    """Build Basic Auth header for upstream Grafana.

    Supports either direct env vars (GRAFANA_USER/GRAFANA_PASS) or
    file-based secrets via GRAFANA_USER_FILE/GRAFANA_PASS_FILE.
    """
    user = os.getenv('GRAFANA_USER')
    pw = os.getenv('GRAFANA_PASS')
    user_file = os.getenv('GRAFANA_USER_FILE')
    pass_file = os.getenv('GRAFANA_PASS_FILE')
    try:
        if user_file and not user and os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                user = f.read().strip()
    except Exception:
        pass
    try:
        if pass_file and not pw and os.path.exists(pass_file):
            with open(pass_file, 'r', encoding='utf-8') as f:
                pw = f.read().strip()
    except Exception:
        pass
    if (user or os.getenv('GRAFANA_USER', '')) and not user:
        # default to 'admin' if only password provided via secret
        user = 'admin'
    if user and pw:
        from base64 import b64encode
        return { 'Authorization': 'Basic ' + b64encode(f"{user}:{pw}".encode()).decode() }
    return {}


@router.get("/grafana/datasources", response_model=dict)
def grafana_datasources(db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = _get_setting(db, 'grafana.url')
    if not base:
        raise HTTPException(status_code=404, detail="grafana.url not configured")
    url = f"{base.rstrip('/')}/api/datasources"
    try:
        r = requests.get(url, timeout=5, headers=_auth_headers())
        return {"url": url, "status": r.status_code, "ok": r.ok, "items": (r.json() if r.ok else None)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/grafana/dashboard/{uid}", response_model=dict)
def grafana_dashboard(uid: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = _get_setting(db, 'grafana.url')
    if not base:
        raise HTTPException(status_code=404, detail="grafana.url not configured")
    url = f"{base.rstrip('/')}/api/dashboards/uid/{uid}"
    try:
        r = requests.get(url, timeout=5, headers=_auth_headers())
        return {"url": url, "status": r.status_code, "ok": r.ok}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/grafana/datasource/{uid}", response_model=dict)
def grafana_datasource_uid(uid: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = _get_setting(db, 'grafana.url')
    if not base:
        raise HTTPException(status_code=404, detail="grafana.url not configured")
    url = f"{base.rstrip('/')}/api/datasources/uid/{uid}"
    try:
        r = requests.get(url, timeout=5, headers=_auth_headers())
        body = r.json() if r.ok else None
        return {"url": url, "status": r.status_code, "ok": r.ok, "body": body}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/grafana/dashboard/slug/{slug}", response_model=dict)
def grafana_dashboard_slug(slug: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = _get_setting(db, 'grafana.url')
    if not base:
        raise HTTPException(status_code=404, detail="grafana.url not configured")
    # Grafana search API by dashboard slug
    url = f"{base.rstrip('/')}/api/search?type=dash-db&query={slug}"
    try:
        r = requests.get(url, timeout=5, headers=_auth_headers())
        items = r.json() if r.ok else None
        # Attempt to find exact slug match
        matched = None
        if isinstance(items, list):
            for it in items:
                if str(it.get('uri','')).endswith(f"/{slug}"):
                    matched = it
                    break
        return {"url": url, "status": r.status_code, "ok": r.ok, "items": items, "match": matched}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
