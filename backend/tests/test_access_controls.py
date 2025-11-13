from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.asset import Asset
from app.models.compliance_result import ComplianceResult
from app.models.tenant import Tenant

from .helpers import ADMIN_USERNAME, ADMIN_PASSWORD

client = TestClient(app)


def _login_admin() -> dict[str, str]:
    resp = client.post(
        "/auth/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _ensure_tenant(slug: str) -> Tenant:
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.slug == slug).first()
        if tenant:
            return tenant
        tenant = Tenant(name=slug, slug=slug, is_active=True)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant
    finally:
        db.close()


def test_assets_endpoint_is_tenant_scoped():
    other_tenant = _ensure_tenant("assets-test")
    db = SessionLocal()
    try:
        db.add_all(
            [
                Asset(
                    tenant_id=1,
                    name="tenant-one-asset",
                    hostname="tenant-one",
                    ip_address="10.0.0.1",
                    os="linux",
                ),
                Asset(
                    tenant_id=other_tenant.id,
                    name="tenant-two-asset",
                    hostname="tenant-two",
                    ip_address="10.0.0.2",
                    os="linux",
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    resp = client.get("/assets", headers=_login_admin())
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data, "Expected at least one asset"
    assert all(item["tenant_id"] == 1 for item in data)
    assert any(item["name"] == "tenant-one-asset" for item in data)
    assert all(item["name"] != "tenant-two-asset" for item in data)


def test_compliance_export_filters_by_tenant():
    other_tenant = _ensure_tenant("compliance-export-test")
    db = SessionLocal()
    try:
        db.add_all(
            [
                ComplianceResult(
                    tenant_id=1,
                    module="tenant-one-module",
                    status="pass",
                    recorded_at=datetime.utcnow(),
                ),
                ComplianceResult(
                    tenant_id=other_tenant.id,
                    module="tenant-two-module",
                    status="fail",
                    recorded_at=datetime.utcnow(),
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    resp = client.get("/compliance/export.csv", headers=_login_admin())
    assert resp.status_code == 200, resp.text
    body = resp.text
    assert "tenant-one-module" in body
    assert "tenant-two-module" not in body
