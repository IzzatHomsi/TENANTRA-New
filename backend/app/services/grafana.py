from __future__ import annotations

import os
from typing import Optional, Tuple, Any
from urllib.parse import urlparse, urlunparse

from sqlalchemy.orm import Session

from app.models.app_setting import AppSetting
from app.core.crypto import decrypt_data
from app.core.secrets import get_enc_key


def _fetch_setting(db: Session, key: str, tenant_id: Optional[int] = None) -> Optional[Any]:
    if tenant_id is not None:
        row = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == tenant_id, AppSetting.key == key)
            .first()
        )
        if row:
            return row.value
    row = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None), AppSetting.key == key)
        .first()
    )
    return row.value if row else None


def _internalize_host(value: str) -> str:
    """
    Allow user-facing configs like https://localhost:3000 while routing internally to the
    Grafana service hostname/port inside Docker.
    """
    try:
        parsed = urlparse(value)
    except Exception:
        return value
    hostname = (parsed.hostname or "").lower()
    if hostname not in {"localhost", "127.0.0.1"}:
        return value
    internal_host = os.getenv("GRAFANA_INTERNAL_HOST", "grafana").strip() or "grafana"
    env_scheme = os.getenv("GRAFANA_INTERNAL_SCHEME")
    if env_scheme:
        internal_scheme = env_scheme.strip() or "http"
    else:
        internal_scheme = "http"
    env_port = os.getenv("GRAFANA_INTERNAL_PORT")
    if env_port:
        internal_port = env_port.strip()
    else:
        internal_port = str(parsed.port or "3000")
    if internal_port in ("80", "443", "", None):
        netloc = internal_host
    else:
        netloc = f"{internal_host}:{internal_port}"
    internal_path = parsed.path or ""
    return urlunparse((internal_scheme, netloc, internal_path, "", "", ""))


def get_base_url(db: Session, tenant_id: Optional[int] = None) -> Optional[str]:
    value = _fetch_setting(db, "grafana.url", tenant_id=tenant_id)
    if isinstance(value, str) and value.strip():
        sanitized = _internalize_host(value.strip())
        return sanitized
    return None


def get_credentials(db: Session, tenant_id: Optional[int] = None) -> Optional[Tuple[str, str]]:
    username = _fetch_setting(db, "grafana.basic.username", tenant_id=tenant_id)
    if not username or not isinstance(username, str):
        return None
    payload = _fetch_setting(db, "grafana.basic.password", tenant_id=tenant_id)
    ciphertext = None
    if isinstance(payload, dict):
        ciphertext = payload.get("ciphertext")
    elif isinstance(payload, str):
        ciphertext = payload
    if not ciphertext:
        return None
    try:
        password = decrypt_data(ciphertext, get_enc_key())
    except Exception:
        return None
    return username, password
