from typing import Any, Dict, Tuple
import hashlib
import json
from urllib.parse import urlparse, urlunparse
from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.app_setting import AppSetting

router = APIRouter(prefix="/support/settings/public", tags=["Public Settings"])

WHITELIST_KEYS = {
    'theme.colors.primary',
    'grafana.url',
    'grafana.dashboard_uid',
    'grafana.datasource_uid',
}


def _sanitize_setting(key: str, value: Any) -> Tuple[Any, Dict[str, Any]]:
    meta: Dict[str, Any] = {"configured": False}
    if key == 'grafana.url':
        sanitized = ""
        if isinstance(value, str):
            raw = value.strip()
            if raw:
                try:
                    parsed = urlparse(raw)
                    if parsed.scheme and parsed.netloc:
                        path = (parsed.path or "").rstrip("/")
                        candidate = urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
                        if parsed.hostname in {'grafana', 'grafana.local'} or (
                            parsed.hostname in {'localhost', '127.0.0.1'} and (parsed.port in {None, 3000})
                        ):
                            sanitized = '/grafana'
                            meta["source"] = "proxy"
                        else:
                            sanitized = candidate
                            meta["source"] = "upstream"
                        meta["configured"] = True
                except Exception:
                    sanitized = ""
        meta["configured"] = bool(sanitized)
        return sanitized, meta
    if key in {'grafana.dashboard_uid', 'grafana.datasource_uid'}:
        if isinstance(value, str):
            sanitized = value.strip()
        else:
            sanitized = ""
        meta["configured"] = bool(sanitized)
        return sanitized, meta
    if key == 'theme.colors.primary':
        if isinstance(value, str):
            sanitized = value.strip()
            if sanitized and not sanitized.startswith("#"):
                sanitized = f"#{sanitized}"
        else:
            sanitized = "#1877f2"
        meta["configured"] = bool(sanitized)
        return sanitized, meta
    # Default passthrough with configured flag
    configured = value not in (None, "", [], {})
    meta["configured"] = bool(configured)
    return value, meta


def _compute_etag(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f'W/"{hashlib.sha256(raw).hexdigest()}"'


@router.get("", response_model=Dict[str, object])
def get_public_settings(response: Response, db: Session = Depends(get_db)) -> Dict[str, object]:
    payload: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    rows = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None))
        .filter(AppSetting.key.in_(list(WHITELIST_KEYS)))
        .all()
    )
    for r in rows:
        sanitized, meta = _sanitize_setting(r.key, r.value)
        if isinstance(r.updated_at, datetime):
            meta["last_updated"] = r.updated_at.isoformat()
        payload[r.key] = sanitized
        metadata[r.key] = meta
    for key in ("grafana.url", "grafana.dashboard_uid", "grafana.datasource_uid"):
        if key not in payload:
            sanitized, meta = _sanitize_setting(key, None)
            payload[key] = sanitized
            metadata[key] = meta
    metadata.setdefault("grafana.url", {"configured": bool(payload.get("grafana.url"))})
    grafana_configured = bool(payload.get("grafana.url"))
    payload["grafana.configured"] = grafana_configured
    metadata["grafana.configured"] = {"configured": grafana_configured}
    payload["_metadata"] = metadata
    response.headers["ETag"] = _compute_etag(payload)
    response.headers.setdefault("Cache-Control", "public, max-age=30")
    return payload
