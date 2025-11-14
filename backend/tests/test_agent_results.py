from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.scan_module_result import ScanModuleResult
from .helpers import ADMIN_PASSWORD, ADMIN_USERNAME


client = TestClient(app)


def _login_admin() -> str:
    resp = client.post("/auth/login", data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    payload = resp.json()
    token = payload.get("access_token")
    assert token
    return token


def test_agent_can_submit_results():
    admin_token = _login_admin()
    modules = client.get("/modules/", headers={"Authorization": f"Bearer {admin_token}"})
    assert modules.status_code == 200
    module_id = modules.json()[0]["id"]

    enroll_resp = client.post(
        "/agents/enroll",
        json={"name": "agent-results-test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert enroll_resp.status_code == 200
    payload = enroll_resp.json()
    agent_id = payload["agent_id"]
    agent_token = payload["token"]

    result_resp = client.post(
        "/agents/results",
        json={
            "agent_id": agent_id,
            "module_id": module_id,
            "status": "success",
            "details": {"summary": "submitted from test"},
        },
        headers={"X-Agent-Token": agent_token},
    )
    assert result_resp.status_code == 201
    record_id = result_resp.json()["id"]

    session = SessionLocal()
    try:
        record = session.query(ScanModuleResult).filter(ScanModuleResult.id == record_id).first()
        assert record is not None
        assert record.agent_id == agent_id
        assert record.module_id == module_id
        assert record.status == "success"
    finally:
        session.close()
