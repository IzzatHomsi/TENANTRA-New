from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.audit_log import AuditLog
from .helpers import ADMIN_USERNAME, ADMIN_PASSWORD

client = TestClient(app)


def _login_admin() -> str:
    response = client.post(
        "/auth/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token
    return token


def test_notification_create_logs_audit_entry():
    token = _login_admin()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Audit Notification",
        "message": "Testing audit trail",
        "recipient_email": "admin@example.com",
    }
    create_resp = client.post("/notifications", json=payload, headers=headers)
    assert create_resp.status_code == 201

    db = SessionLocal()
    try:
        audit_rows = (
            db.query(AuditLog)
            .filter(AuditLog.action == "notification.create")
            .order_by(AuditLog.id.desc())
            .all()
        )
    finally:
        db.close()
    assert audit_rows, "Expected audit log entry for notification.create"

    audit_resp = client.get("/audit-logs", headers=headers)
    assert audit_resp.status_code == 200
    body = audit_resp.json()
    assert any(item.get("action") == "notification.create" for item in body.get("items", []))


def test_audit_log_export_handles_bad_ciphertext():
    token = _login_admin()
    headers = {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    try:
        db.add(AuditLog(user_id=1, action="ciphertext-test", result="success", details_enc="not-base64-data"))
        db.commit()
    finally:
        db.close()

    resp = client.get("/audit-logs/export", headers=headers)
    assert resp.status_code == 200
