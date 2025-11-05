"""Feature flags bootstrap endpoint.

Returns a map of UI/feature flags based on role/tenant and optional app settings.
"""

from __future__ import annotations

from typing import Dict, List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.models.user import User
from app.models.app_setting import AppSetting
from app.database import get_db


router = APIRouter(prefix="/features", tags=["Public Settings"])


def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in (src or {}).items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


@router.get("")
def get_features(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, bool]:
    is_admin = current_user.role in {"admin", "administrator", "super_admin", "system_admin", "msp_admin"}
    # Defaults; extend with AppSetting-driven toggles as needed.
    flags: Dict[str, Any] = {
        "notificationHistory": True,
        "auditLogs": is_admin,
        "threatIntel": True,
        "billing": is_admin,
        "tenants": is_admin,
        "settings": is_admin,
        "alertSettings": is_admin,
        "featureFlags": is_admin,
        # Optional modules
        "assets": False,
        "scanSchedules": True,
        "reports": False,
    }
    # Overlay with AppSetting flags (global first, then tenant overrides)
    try:
        # Global nested map (key == 'features')
        q_global_map: List[AppSetting] = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id.is_(None))
            .filter(AppSetting.key == "features")
            .all()
        )
        for row in q_global_map:
            if isinstance(row.value, dict):
                _deep_merge(flags, row.value)
        # Global individual flags (key starts with 'features.')
        q_global: List[AppSetting] = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id.is_(None))
            .filter(AppSetting.key.like("features.%"))
            .all()
        )
        for row in q_global:
            name = row.key.split(".", 1)[1]
            if isinstance(row.value, (bool, int)):
                flags[name] = bool(row.value)
        if current_user.tenant_id is not None:
            # Tenant nested map
            q_tenant_map: List[AppSetting] = (
                db.query(AppSetting)
                .filter(AppSetting.tenant_id == current_user.tenant_id)
                .filter(AppSetting.key == "features")
                .all()
            )
            for row in q_tenant_map:
                if isinstance(row.value, dict):
                    _deep_merge(flags, row.value)
            # Tenant individual flags
            q_tenant: List[AppSetting] = (
                db.query(AppSetting)
                .filter(AppSetting.tenant_id == current_user.tenant_id)
                .filter(AppSetting.key.like("features.%"))
                .all()
            )
            for row in q_tenant:
                name = row.key.split(".", 1)[1]
                if isinstance(row.value, (bool, int)):
                    flags[name] = bool(row.value)
    except Exception:
        # Non-fatal: keep defaults when settings are unavailable
        pass
    return flags
