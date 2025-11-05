from datetime import datetime
import uuid

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.module import Module
from app.models.scan_module_result import ScanModuleResult
from app.models.tenant_module import TenantModule

client = TestClient(app)


def _login_admin() -> str:
    resp = client.post("/auth/login", data={"username": "admin", "password": "Admin@1234"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token
    return token


def _get_module_id(slug: str) -> int:
    db = SessionLocal()
    try:
        module = db.query(Module).filter(Module.name == slug).first()
        assert module is not None, f"Module {slug} not found in database"
        return module.id
    finally:
        db.close()


def _cleanup_module(module_id: int) -> None:
    db = SessionLocal()
    try:
        record = db.get(Module, module_id)
        if record:
            db.query(TenantModule).filter(TenantModule.module_id == module_id).delete(synchronize_session=False)
            db.delete(record)
            db.commit()
    finally:
        db.close()


def test_run_cis_benchmark_success():
    token = _login_admin()
    module_id = _get_module_id("cis_benchmark")
    payload = {"parameters": {"compliant": True}}

    resp = client.post(
        f"/module-runs/{module_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "success"
    assert body["module_id"] == module_id
    assert "summary" in body["details"]

    db = SessionLocal()
    try:
        record = db.get(ScanModuleResult, body["id"])
        assert record is not None
        assert record.status == "success"
    finally:
        db.close()


def test_run_pci_dss_check_failure():
    token = _login_admin()
    module_id = _get_module_id("pci_dss_check")
    payload = {"parameters": {"encryption_enabled": False, "segmentation_verified": True}}

    resp = client.post(
        f"/module-runs/{module_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "failed"
    assert "details" in body
    assert any("encryption" in item for item in body["details"].get("details", []))

    db = SessionLocal()
    try:
        record = db.get(ScanModuleResult, body["id"])
        assert record is not None
        assert record.status == "failed"
    finally:
        db.close()


def test_run_networking_devices_module_success():
    token = _login_admin()
    db = SessionLocal()
    module_name = f"network_device_health_{uuid.uuid4().hex[:6]}"
    try:
        module = Module(
            name=module_name,
            category="Networking Devices",
            status="active",
            enabled=True,
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        module_id = module.id
    finally:
        db.close()

    payload = {"parameters": {"targets": ["fw-core-1", "edge-router"], "issues": []}}
    resp = client.post(
        f"/module-runs/{module_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "success"
    assert body["details"].get("category") == "Networking Devices"
    assert "targets" in body["details"]

    _cleanup_module(module_id)


def test_run_networking_devices_module_failure():
    token = _login_admin()
    db = SessionLocal()
    module_name = f"network_device_failure_{uuid.uuid4().hex[:6]}"
    try:
        module = Module(
            name=module_name,
            category="Networking Devices",
            status="active",
            enabled=True,
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        module_id = module.id
    finally:
        db.close()

    payload = {"parameters": {"issues": ["interface Gi0/1 down"], "targets": ["core-switch-1"]}}
    resp = client.post(
        f"/module-runs/{module_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "failed"
    assert "findings" in body["details"]

    _cleanup_module(module_id)

def test_run_generic_module_success():
    token = _login_admin()
    db = SessionLocal()
    module_name = f"generic_module_{uuid.uuid4().hex[:6]}"
    try:
        module = Module(
            name=module_name,
            category="Custom Category",
            phase=7,
            status="active",
            enabled=True,
            purpose="Validate custom controls",
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        module_id = module.id
    finally:
        db.close()

    payload = {"parameters": {"notes": "automated check"}}
    resp = client.post(
        f"/module-runs/{module_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "success"
    assert body["details"].get("purpose") == "Validate custom controls"

    _cleanup_module(module_id)



def test_run_network_perimeter_module_success():
    token = _login_admin()
    db = SessionLocal()
    module_name = f"network_perimeter_{uuid.uuid4().hex[:6]}"
    try:
        module = Module(
            name=module_name,
            category="Network & Perimeter Security",
            status="active",
            enabled=True,
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        module_id = module.id
    finally:
        db.close()

    resp = client.post(
        f"/module-runs/{module_id}",
        json={"parameters": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] in {"success", "failed"}
    assert body["module_id"] == module_id

    _cleanup_module(module_id)
