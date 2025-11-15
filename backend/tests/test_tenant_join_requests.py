from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.models.tenant_join_request import TenantJoinRequest
from app.models.user import User


client = TestClient(app)


def _seed_tenant_with_admin():
    db = SessionLocal()
    tenant_slug = f"join-{uuid4().hex[:6]}"
    admin_username = f"join_admin_{uuid4().hex[:5]}"
    admin_password = "Advanc3dPass!"
    tenant = Tenant(name=f"Join {tenant_slug}", slug=tenant_slug, is_active=True)
    db.add(tenant)
    db.flush()
    admin = User(
        username=admin_username,
        email=f"{admin_username}@example.com",
        password_hash=get_password_hash(admin_password),
        role="admin",
        tenant_id=tenant.id,
        is_active=True,
        email_verified_at=datetime.utcnow(),
    )
    db.add(admin)
    db.commit()
    db.refresh(tenant)
    db.refresh(admin)
    db.close()
    return tenant, admin, admin_password


def _cleanup_records(tenant_id: int, admin_id: int):
    db = SessionLocal()
    try:
        db.query(TenantJoinRequest).filter(TenantJoinRequest.tenant_id == tenant_id).delete()
        user = db.query(User).filter(User.id == admin_id).first()
        if user:
            db.delete(user)
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            db.delete(tenant)
        db.commit()
    finally:
        db.close()


def test_tenant_join_request_flow():
    tenant, admin, admin_password = _seed_tenant_with_admin()
    try:
        request_payload = {
            "tenant_identifier": tenant.slug,
            "full_name": "Test Requestor",
            "email": "requestor@example.com",
            "message": "Please add me.",
        }
        create_resp = client.post("/tenants/join-requests", json=request_payload)
        assert create_resp.status_code == 202, create_resp.text

        login_resp = client.post("/auth/login", data={"username": admin.username, "password": admin_password})
        assert login_resp.status_code == 200, login_resp.text
        access_token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        list_resp = client.get("/admin/tenant-join-requests", headers=headers)
        assert list_resp.status_code == 200, list_resp.text
        items = list_resp.json()
        assert any(req["email"] == "requestor@example.com" for req in items)
        request_id = next(req["id"] for req in items if req["email"] == "requestor@example.com")

        decision_resp = client.post(
            f"/admin/tenant-join-requests/{request_id}/decision",
            headers=headers,
            json={"decision": "approved", "note": "Welcome aboard"},
        )
        assert decision_resp.status_code == 200, decision_resp.text
        assert decision_resp.json()["status"] == "approved"
    finally:
        _cleanup_records(tenant.id, admin.id)
