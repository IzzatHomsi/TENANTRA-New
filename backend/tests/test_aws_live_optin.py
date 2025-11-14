import os
import pytest
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


def _create_module(slug: str, category: str = "Identity & Access Scanning", phase: int = 2) -> int:
    db = SessionLocal()
    try:
        m = Module(
            name=slug,
            external_id=slug,
            category=category,
            phase=phase,
            status=ModuleStatus.ACTIVE,
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


@pytest.mark.skipif(
    os.getenv("ENABLE_AWS_LIVE_TESTS", "0").strip().lower() not in {"1", "true", "yes", "on"},
    reason="AWS live tests disabled; set ENABLE_AWS_LIVE_TESTS=true to run",
)
def test_aws_iam_live_opt_in_runs():
    os.environ["TENANTRA_ENABLE_AWS_LIVE"] = "true"
    token = _login_admin()
    module_id = _create_module("aws-iam-baseline")
    try:
        resp = client.post(
            f"/module-runs/{module_id}",
            json={"parameters": {}},
            headers={"Authorization": f"Bearer {token}"},
        )
        # The live runner may return success/failed/skipped depending on creds/boto3.
        assert resp.status_code == 201
        body = resp.json()
        assert body.get("details", {}).get("service") == "aws-iam"
        assert body["status"] in {"success", "failed", "skipped"}
    finally:
        _delete_module(module_id)
        os.environ.pop("TENANTRA_ENABLE_AWS_LIVE", None)
