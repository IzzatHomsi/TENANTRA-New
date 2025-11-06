from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.app_setting import AppSetting
from app.models.audit_log import AuditLog
from app.utils.audit import log_audit_event


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
    original_url_value = original_url.value if original_url else None
    original_dashboard_value = original_dashboard.value if original_dashboard else None
    original_features_value = original_features.value if original_features else None
    try:
        payload = {
            "grafana.url": "https://grafana.example.com/dashboard/",
            "grafana.dashboard_uid": "test-dash",
            "features": {"observability": True},
        }
        resp = client.put("/admin/settings", headers=headers, json=payload)
        assert resp.status_code == 200
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
