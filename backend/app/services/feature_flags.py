from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.app_setting import AppSetting
from app.models.user import User

_ADMIN_ROLES = {"admin", "administrator", "super_admin", "system_admin", "msp_admin"}
_READONLY_ROLES = {"auditor", "audit", "read_only_admin"}


def _deep_merge(dst: Dict[str, Any], src: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(src, dict):
        return dst
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            _deep_merge(dst[key], value)
        else:
            dst[key] = value
    return dst


def _fetch_feature_map(db: Session, tenant_id: Optional[int]) -> Dict[str, Any]:
    """Load merged feature flags for the provided tenant (global overlaid with tenant overrides)."""
    flags: Dict[str, Any] = {}

    def _merge_scope(query):
        scoped: Dict[str, Any] = {}
        for row in query:
            if row.key == "features" and isinstance(row.value, dict):
                _deep_merge(scoped, row.value)
            elif row.key.startswith("features.") and isinstance(row.value, (bool, int)):
                scoped[row.key.split(".", 1)[1]] = bool(row.value)
        return scoped

    global_rows = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None))
        .filter(AppSetting.key.in_(["features"]))
        .all()
    )
    _deep_merge(flags, _merge_scope(global_rows))

    global_individual = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None))
        .filter(AppSetting.key.like("features.%"))
        .all()
    )
    _deep_merge(flags, _merge_scope(global_individual))

    if tenant_id is not None:
        tenant_rows = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == tenant_id)
            .filter(AppSetting.key.in_(["features"]))
            .all()
        )
        _deep_merge(flags, _merge_scope(tenant_rows))

        tenant_individual = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == tenant_id)
            .filter(AppSetting.key.like("features.%"))
            .all()
        )
        _deep_merge(flags, _merge_scope(tenant_individual))

    return flags


class SettingsAccess:
    """Simple enum-like helper for settings access levels."""

    DENIED = "denied"
    READ = "read"
    WRITE = "write"


def resolve_settings_access(db: Session, user: User) -> str:
    """Determine whether the user can read or write App Settings."""

    role = (getattr(user, "role", "") or "").strip().lower()
    if role in _ADMIN_ROLES:
        mode = SettingsAccess.WRITE
    elif role in _READONLY_ROLES:
        mode = SettingsAccess.READ
    else:
        mode = SettingsAccess.DENIED

    flags = _fetch_feature_map(db, user.tenant_id)

    settings_flag = flags.get("settings")
    if settings_flag is False:
        return SettingsAccess.DENIED

    readonly_flag = flags.get("settings.readonly")
    if readonly_flag:
        if mode == SettingsAccess.DENIED:
            return SettingsAccess.READ
        return SettingsAccess.READ

    write_flag = flags.get("settings.write")
    if write_flag is False and mode == SettingsAccess.WRITE:
        return SettingsAccess.READ

    return mode


def ensure_settings_read_access(db: Session, user: User) -> None:
    if resolve_settings_access(db, user) == SettingsAccess.DENIED:
        raise PermissionError("Settings feature disabled for this user")


def ensure_settings_write_access(db: Session, user: User) -> None:
    mode = resolve_settings_access(db, user)
    if mode == SettingsAccess.DENIED:
        raise PermissionError("Settings feature disabled for this user")
    if mode != SettingsAccess.WRITE:
        raise PermissionError("Settings are read-only for this user")


__all__ = [
    "resolve_settings_access",
    "SettingsAccess",
    "ensure_settings_read_access",
    "ensure_settings_write_access",
]
