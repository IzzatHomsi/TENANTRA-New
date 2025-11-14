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
            category="Identity & Access Scanning",
            phase=2,
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


def test_aws_iam_baseline_success():
    token = _login_admin()
    module_id = _create_module("aws-iam-baseline")
    try:
        payload = {
            "parameters": {
                "users": [
                    {"username": "alice", "mfa_enabled": True, "access_keys": [{"age_days": 10, "active": True}]},
                    {"username": "bob", "mfa_enabled": True, "access_keys": []},
                ],
                "max_key_age_days": 90,
            }
        }
        resp = client.post(
            f"/module-runs/{module_id}",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "success"
        assert body["details"]["summary"]["users_checked"] == 2
        assert body["details"]["summary"]["mfa_missing"] == 0
        assert body["details"]["summary"]["old_keys"] == 0
    finally:
        _delete_module(module_id)


def test_aws_iam_baseline_failure():
    token = _login_admin()
    module_id = _create_module("aws-iam-baseline")
    try:
        payload = {
            "parameters": {
                "users": [
                    {"username": "carol", "mfa_enabled": False, "access_keys": []},
                    {"username": "dave", "mfa_enabled": True, "access_keys": [{"age_days": 200, "active": True}]},
                ],
                "max_key_age_days": 90,
            }
        }
        resp = client.post(
            f"/module-runs/{module_id}",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "failed"
        assert any(f.get("issue") == "mfa_missing" for f in body["details"].get("findings", []))
        assert any(f.get("issue") == "access_key_too_old" for f in body["details"].get("findings", []))
    finally:
        _delete_module(module_id)
