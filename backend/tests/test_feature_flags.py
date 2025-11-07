from __future__ import annotations

import pytest

from sqlalchemy import or_

from app.database import SessionLocal
from app.models.app_setting import AppSetting
from app.models.user import User
from app.services.feature_flags import (
    SettingsAccess,
    ensure_settings_read_access,
    ensure_settings_write_access,
    resolve_settings_access,
)


def _make_user(*, role: str, tenant_id: int | None = 1) -> User:
    return User(
        id=999,
        username=f"{role}-user",
        password_hash="hash",
        role=role,
        tenant_id=tenant_id,
        is_active=True,
    )


@pytest.fixture(autouse=True)
def _clean_app_settings():
    db = SessionLocal()
    try:
        db.query(AppSetting).filter(
            or_(
                AppSetting.key == "features",
                AppSetting.key.like("features.%"),
            )
        ).delete(synchronize_session=False)
        db.commit()
        yield
    finally:
        db.close()


def _set_flag(key: str, value: bool, *, tenant_id: int | None = None) -> None:
    db = SessionLocal()
    try:
        db.add(AppSetting(tenant_id=tenant_id, key=key, value=value))
        db.commit()
    finally:
        db.close()


def test_admin_defaults_to_write_access():
    db = SessionLocal()
    try:
        access = resolve_settings_access(db, _make_user(role="admin"))
        assert access == SettingsAccess.WRITE
    finally:
        db.close()


def test_settings_feature_disabled_blocks_all_access():
    _set_flag("features.settings", False)
    db = SessionLocal()
    user = _make_user(role="admin")
    try:
        assert resolve_settings_access(db, user) == SettingsAccess.DENIED
        with pytest.raises(PermissionError):
            ensure_settings_read_access(db, user)
        with pytest.raises(PermissionError):
            ensure_settings_write_access(db, user)
    finally:
        db.close()


def test_readonly_flag_downgrades_admin():
    _set_flag("features.settings.readonly", True)
    db = SessionLocal()
    user = _make_user(role="admin")
    try:
        assert resolve_settings_access(db, user) == SettingsAccess.READ
        ensure_settings_read_access(db, user)
        with pytest.raises(PermissionError):
            ensure_settings_write_access(db, user)
    finally:
        db.close()


def test_write_flag_false_disables_mutations_but_allows_reads():
    _set_flag("features.settings.write", False)
    db = SessionLocal()
    user = _make_user(role="admin")
    try:
        assert resolve_settings_access(db, user) == SettingsAccess.READ
        ensure_settings_read_access(db, user)
        with pytest.raises(PermissionError):
            ensure_settings_write_access(db, user)
    finally:
        db.close()


def test_tenant_override_applies_on_top_of_global_flags():
    _set_flag("features.settings", True)
    _set_flag("features.settings", False, tenant_id=42)
    db = SessionLocal()
    tenant_admin = _make_user(role="admin", tenant_id=42)
    try:
        assert resolve_settings_access(db, tenant_admin) == SettingsAccess.DENIED
    finally:
        db.close()


def test_auditor_role_defaults_to_read_access():
    db = SessionLocal()
    readonly = _make_user(role="auditor")
    try:
        assert resolve_settings_access(db, readonly) == SettingsAccess.READ
        ensure_settings_read_access(db, readonly)
        with pytest.raises(PermissionError):
            ensure_settings_write_access(db, readonly)
    finally:
        db.close()


def test_non_privileged_role_denied_without_flags():
    db = SessionLocal()
    standard_user = _make_user(role="standard_user")
    try:
        assert resolve_settings_access(db, standard_user) == SettingsAccess.DENIED
        with pytest.raises(PermissionError):
            ensure_settings_read_access(db, standard_user)
    finally:
        db.close()
