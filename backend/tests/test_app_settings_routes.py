from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.app_setting import AppSetting
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.audit import log_audit_event
from app.core.auth import create_access_token


client = TestClient(app)


def _login_admin() -> dict[str, str]:
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "Admin@1234"},
    )
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token
    return {"Authorization": f"Bearer {token}"}


def _create_user_with_role(*, username: str, role: str, tenant_id: int | None = 1) -> tuple[int, dict[str, str]]:
    db = SessionLocal()
    try:
        user = User(
            username=username,
            password_hash="test-hash",
            role=role,
            tenant_id=tenant_id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token({"sub": str(user.id)})
        return user.id, {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


def _delete_user(user_id: int) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def _get_setting(db, key: str) -> AppSetting | None:
    return (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None))
        .filter(AppSetting.key == key)
        .one_or_none()
    )


def test_app_settings_reject_invalid_payload():
    headers = _login_admin()
    resp = client.put("/admin/settings", headers=headers, json={"grafana.url": "grafana.example.com"})
    assert resp.status_code == 422
    detail = resp.json()
    assert any(err["loc"][-1] == "grafana.url" for err in detail)

    resp_unknown = client.put("/admin/settings", headers=headers, json={"unknown.setting": True})
    assert resp_unknown.status_code == 422


def test_app_settings_update_sanitizes_and_logs_changes():
    headers = _login_admin()
    db = SessionLocal()
    original_url = _get_setting(db, "grafana.url")
    original_dashboard = _get_setting(db, "grafana.dashboard_uid")
    original_features = _get_setting(db, "features")
    original_username = _get_setting(db, "grafana.basic.username")
    original_password = _get_setting(db, "grafana.basic.password")
    original_url_value = original_url.value if original_url else None
    original_dashboard_value = original_dashboard.value if original_dashboard else None
    original_features_value = original_features.value if original_features else None
    original_username_value = original_username.value if original_username else None
    original_password_value = original_password.value if original_password else None
    try:
        payload = {
            "grafana.url": "https://grafana.example.com/dashboard/",
            "grafana.dashboard_uid": "test-dash",
            "features": {"observability": True},
            "grafana.basic.username": "svc-grafana",
            "grafana.basic.password": "Secret123!",
        }
        resp = client.put("/admin/settings", headers=headers, json=payload)
        assert resp.status_code == 200
        write_snapshot = resp.json()
        assert any(item["key"] == "grafana.url" for item in write_snapshot)
        password_item = next((item for item in write_snapshot if item["key"] == "grafana.basic.password"), None)
        assert password_item is not None
        assert password_item["value"].get("set") is True
        refreshed = client.get("/admin/settings", headers=headers)
        assert refreshed.status_code == 200
        settings_map = {item["key"]: item["value"] for item in refreshed.json()}
        assert settings_map["grafana.url"] == "https://grafana.example.com/dashboard"
        assert settings_map["grafana.dashboard_uid"] == "test-dash"
        public = client.get("/support/settings/public")
        assert public.status_code == 200
        public_json = public.json()
        assert public_json["grafana.url"] in {"https://grafana.example.com/dashboard", "/grafana"}
        assert public_json["grafana.configured"] is True
        assert "_metadata" in public_json
        audit_entry = (
            db.query(AuditLog)
            .filter(AuditLog.action == "app_settings.update")
            .order_by(AuditLog.id.desc())
            .first()
        )
        assert audit_entry is not None
        details = audit_entry.details
        assert details and "grafana.url" in details
        stored_password = _get_setting(db, "grafana.basic.password")
        assert stored_password is not None and isinstance(stored_password.value, dict)
        assert "ciphertext" in stored_password.value
    finally:
        db.close()
        restore = SessionLocal()
        try:
            row = _get_setting(restore, "grafana.url")
            if original_url_value is None:
                if row:
                    restore.delete(row)
            else:
                if row:
                    row.value = original_url_value
                else:
                    restore.add(AppSetting(tenant_id=None, key="grafana.url", value=original_url_value))

            dash_row = _get_setting(restore, "grafana.dashboard_uid")
            if original_dashboard_value is None:
                if dash_row:
                    restore.delete(dash_row)
            else:
                if dash_row:
                    dash_row.value = original_dashboard_value
                else:
                    restore.add(AppSetting(tenant_id=None, key="grafana.dashboard_uid", value=original_dashboard_value))

            features_row = _get_setting(restore, "features")
            if original_features_value is None:
                if features_row:
                    restore.delete(features_row)
            else:
                if features_row:
                    features_row.value = original_features_value
                else:
                    restore.add(AppSetting(tenant_id=None, key="features", value=original_features_value))

            username_row = _get_setting(restore, "grafana.basic.username")
            if original_username_value is None:
                if username_row:
                    restore.delete(username_row)
            else:
                if username_row:
                    username_row.value = original_username_value
                else:
                    restore.add(AppSetting(tenant_id=None, key="grafana.basic.username", value=original_username_value))

            password_row = _get_setting(restore, "grafana.basic.password")
            if original_password_value is None:
                if password_row:
                    restore.delete(password_row)
            else:
                if password_row:
                    password_row.value = original_password_value
                else:
                    restore.add(AppSetting(tenant_id=None, key="grafana.basic.password", value=original_password_value))
            restore.commit()
        finally:
            restore.close()


def test_grafana_health_missing_configuration_returns_soft_payload():
    headers = _login_admin()
    db = SessionLocal()
    row = _get_setting(db, "grafana.url")
    original_value = row.value if row else None
    try:
        if row:
            db.delete(row)
            db.commit()
        resp = client.get("/admin/observability/grafana/health", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["configured"] is False
        assert body["ok"] is False
        assert body.get("status") == 424
    finally:
        db.close()
        restore = SessionLocal()
        try:
            if original_value is not None:
                existing = _get_setting(restore, "grafana.url")
                if existing:
                    existing.value = original_value
                else:
                    restore.add(AppSetting(tenant_id=None, key="grafana.url", value=original_value))
                restore.commit()
        finally:
            restore.close()


def test_audit_logs_ordering_respects_created_at():
    headers = _login_admin()
    base_time = datetime.utcnow() - timedelta(minutes=5)
    db = SessionLocal()
    try:
        log_audit_event(
            db,
            user_id=None,
            action="ordering.first",
            result="success",
            timestamp=base_time,
            details={"marker": "first"},
        )
        log_audit_event(
            db,
            user_id=None,
            action="ordering.second",
            result="success",
            timestamp=base_time + timedelta(minutes=1),
            details={"marker": "second"},
        )
    finally:
        db.close()
    resp = client.get("/audit-logs?page=1&page_size=5", headers=headers)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["items"], "Expected audit log items"
    actions = [item["action"] for item in payload["items"]]
    assert actions[0] == "ordering.second"


def test_auditor_can_read_but_not_write_settings():
    user_id, headers = _create_user_with_role(username="auditor-user", role="auditor")
    try:
        resp_get = client.get("/admin/settings", headers=headers)
        assert resp_get.status_code == 200
        resp_put = client.put("/admin/settings", headers=headers, json={"theme.colors.primary": "#102030"})
        assert resp_put.status_code == 403
    finally:
        _delete_user(user_id)


def test_tenant_settings_update_validation():
    headers = _login_admin()
    bad = client.put("/admin/settings/tenant", headers=headers, json={"grafana.url": "not-a-url"})
    assert bad.status_code == 422

    update_payload = {
        "networking.dhcp.scopes": [
            {
                "name": "QA-Lab",
                "total_leases": 32,
                "active_leases": 10,
                "reserved_leases": 2,
                "tags": ["lab"],
            }
        ],
    }
    ok = client.put("/admin/settings/tenant", headers=headers, json=update_payload)
    assert ok.status_code == 200
    tenant_snapshot = ok.json()
    assert any(item["key"] == "networking.dhcp.scopes" for item in tenant_snapshot)

    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        tenant_id = admin_user.tenant_id if admin_user else None
        if tenant_id is not None:
            row = (
                db.query(AppSetting)
                .filter(AppSetting.tenant_id == tenant_id, AppSetting.key == "networking.dhcp.scopes")
                .first()
            )
            if row:
                db.delete(row)
                db.commit()
    finally:
        db.close()
