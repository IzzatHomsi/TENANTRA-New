from __future__ import annotations

from typing import Optional, Tuple, Any

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


def get_base_url(db: Session, tenant_id: Optional[int] = None) -> Optional[str]:
    value = _fetch_setting(db, "grafana.url", tenant_id=tenant_id)
    if isinstance(value, str) and value.strip():
        return value
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
