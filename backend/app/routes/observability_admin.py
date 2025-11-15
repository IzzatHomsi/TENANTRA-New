from typing import Optional, Dict, Any
import logging
import os
import threading
import time
from contextlib import nullcontext

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.user import User
from app.observability.metrics import record_grafana_health, record_grafana_misconfig
from app.services.grafana import get_base_url, get_credentials
from app.services.grafana_warnings import list_grafana_warnings

router = APIRouter(prefix="/admin/observability", tags=["Admin Observability"])
logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace as otel_trace

    _TRACER = otel_trace.get_tracer(__name__)
except Exception:  # pragma: no cover - optional dependency
    _TRACER = None


def _span(name: str):
    if _TRACER:
        return _TRACER.start_as_current_span(name)
    return nullcontext()


_HTTP_TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=5.0)


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
async def grafana_health(db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = get_base_url(db)
    if not base:
        record_grafana_health(False)
        record_grafana_misconfig()
        logger.warning("Grafana health check aborted: grafana.url app setting not configured")
        cached = _GRAFANA_HEALTH_STATE.cached("missing-config")
        payload = {
            "ok": False,
            "configured": False,
            "status": status.HTTP_424_FAILED_DEPENDENCY,
            "detail": {"message": "grafana.url not configured", "configured": False},
            "checked_at": time.time(),
            "message": "grafana.url not configured",
        }
        if cached:
            cached["configured"] = False
            cached.setdefault("ok", False)
            cached.setdefault("status", status.HTTP_424_FAILED_DEPENDENCY)
            cached.setdefault("detail", {"message": "grafana.url not configured", "configured": False})
            return cached
        return _GRAFANA_HEALTH_STATE.record_result(payload)
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
    headers = _auth_headers(db)
    _GRAFANA_HEALTH_STATE.mark_attempt()
    with _span("grafana.health") as span:
        if span is not None:
            span.set_attribute("grafana.url", url)
        try:
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, follow_redirects=False) as client:
                response = await client.get(url, headers=headers)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            payload = {
                "url": url,
                "grafana_url": base,
                "status": response.status_code,
                "ok": response.is_success,
                "message": "Grafana API healthy" if response.is_success else "Grafana API returned error",
                "body": response.text[:200] if response.text else None,
                "checked_at": time.time(),
                "latency_ms": latency_ms,
                "configured": True,
            }
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("tenantra.grafana.ok", response.is_success)
                span.set_attribute("tenantra.grafana.latency_ms", latency_ms)
            return _GRAFANA_HEALTH_STATE.record_result(payload)
        except httpx.HTTPError as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            payload = {
                "url": url,
                "grafana_url": base,
                "status": 502,
                "ok": False,
                "message": "Grafana API request failed",
                "error": str(exc),
                "checked_at": time.time(),
                "latency_ms": latency_ms,
                "configured": True,
            }
            if span is not None:
                span.record_exception(exc)
                span.set_attribute("http.status_code", 502)
                span.set_attribute("tenantra.grafana.ok", False)
                span.set_attribute("tenantra.grafana.latency_ms", latency_ms)
            _GRAFANA_HEALTH_STATE.record_result(payload)
            cached = _GRAFANA_HEALTH_STATE.cached("exception")
            if cached:
                return cached
            raise HTTPException(status_code=502, detail=str(exc))


def _auth_headers(db: Session) -> dict:
    """Build Basic Auth header for upstream Grafana.

    Supports either direct env vars (GRAFANA_USER/GRAFANA_PASS) or
    file-based secrets via GRAFANA_USER_FILE/GRAFANA_PASS_FILE.
    """
    cred = get_credentials(db)
    if cred:
        user, pw = cred
        from base64 import b64encode

        return {'Authorization': 'Basic ' + b64encode(f"{user}:{pw}".encode()).decode()}
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


async def _grafana_get(db: Session, base: str, path: str, *, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
    url = f"{base.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, follow_redirects=False) as client:
        return await client.get(url, headers=_auth_headers(db), params=params)


@router.get("/grafana/datasources", response_model=dict)
async def grafana_datasources(db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = get_base_url(db)
    if not base:
        raise HTTPException(status_code=404, detail="grafana.url not configured")
    try:
        response = await _grafana_get(db, base, "api/datasources")
        url = str(response.request.url)
        items = response.json() if response.is_success else None
        return {"url": url, "status": response.status_code, "ok": response.is_success, "items": items}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/grafana/dashboard/{uid}", response_model=dict)
async def grafana_dashboard(uid: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = get_base_url(db)
    if not base:
        raise HTTPException(status_code=404, detail="grafana.url not configured")
    try:
        response = await _grafana_get(db, base, f"api/dashboards/uid/{uid}")
        url = str(response.request.url)
        return {"url": url, "status": response.status_code, "ok": response.is_success}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/grafana/warnings", response_model=dict)
async def grafana_warnings(limit: int = 20, _: User = Depends(get_admin_user)) -> dict:
    """Expose recent Grafana proxy warnings so UI surfaces loadDashboardScene issues."""
    items = list_grafana_warnings(max(limit, 0))
    return {"items": items}


@router.get("/grafana/datasource/{uid}", response_model=dict)
async def grafana_datasource_uid(uid: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = get_base_url(db)
    if not base:
        raise HTTPException(status_code=404, detail="grafana.url not configured")
    try:
        response = await _grafana_get(db, base, f"api/datasources/uid/{uid}")
        url = str(response.request.url)
        body = response.json() if response.is_success else None
        return {"url": url, "status": response.status_code, "ok": response.is_success, "body": body}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/grafana/dashboard/slug/{slug}", response_model=dict)
async def grafana_dashboard_slug(slug: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    base = get_base_url(db)
    if not base:
        raise HTTPException(status_code=404, detail="grafana.url not configured")
    try:
        response = await _grafana_get(db, base, "api/search", params={"type": "dash-db", "query": slug})
        url = str(response.request.url)
        items = response.json() if response.is_success else None
        # Attempt to find exact slug match
        matched = None
        if isinstance(items, list):
            for it in items:
                if str(it.get('uri','')).endswith(f"/{slug}"):
                    matched = it
                    break
        return {"url": url, "status": response.status_code, "ok": response.is_success, "items": items, "match": matched}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))
