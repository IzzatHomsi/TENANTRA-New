import os
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.module import Module, ModuleStatus
from .helpers import ADMIN_USERNAME, ADMIN_PASSWORD


client = TestClient(app)


def _login_admin() -> str:
    resp = client.post("/auth/login", data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _create_module(slug: str) -> int:
    db = SessionLocal()
    try:
        m = Module(
            name=slug,
            external_id=slug,
            category="Networking Devices",
            phase=3,
            status=ModuleStatus.ACTIVE,
            enabled=True,
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        return m.id
    finally:
        db.close()


def _delete_module(module_id: int) -> None:
    db = SessionLocal()
    try:
        rec = db.get(Module, module_id)
        if rec:
            db.delete(rec)
            db.commit()
    finally:
        db.close()


def test_panorama_stub_skipped_by_default():
    # ensure disabled
    os.environ.pop("TENANTRA_ENABLE_PANORAMA_STUB", None)
    token = _login_admin()
    module_id = _create_module("panorama-policy-drift")
    try:
        resp = client.post(
            f"/module-runs/{module_id}",
            json={"parameters": {"device_group": "DG-Core"}},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "skipped"
        assert body["details"].get("reason") == "stub_disabled"
    finally:
        _delete_module(module_id)


def test_panorama_stub_success_when_enabled():
    os.environ["TENANTRA_ENABLE_PANORAMA_STUB"] = "true"
    token = _login_admin()
    module_id = _create_module("panorama-policy-drift")
    try:
        resp = client.post(
            f"/module-runs/{module_id}",
            json={"parameters": {"device_group": "DG-Core"}},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "success"
        assert body["details"]["summary"]["device_group"] == "DG-Core"
    finally:
        _delete_module(module_id)
        os.environ.pop("TENANTRA_ENABLE_PANORAMA_STUB", None)
