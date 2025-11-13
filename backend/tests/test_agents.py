from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.agent import Agent

from .helpers import ADMIN_USERNAME, ADMIN_PASSWORD

client = TestClient(app)


def _login_admin() -> dict[str, str]:
    resp = client.post("/auth/login", data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_agent_config_requires_valid_token():
    db = SessionLocal()
    try:
        agent = Agent(
            tenant_id=1,
            name="cfg-agent",
            token="abc123token",
            status="active",
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        agent_id = agent.id
    finally:
        db.close()

    missing = client.get(f"/agents/config/{agent_id}")
    assert missing.status_code == 422

    wrong = client.get(f"/agents/config/{agent_id}", headers={"X-Agent-Token": "wrong"})
    assert wrong.status_code == 401

    ok = client.get(f"/agents/config/{agent_id}", headers={"X-Agent-Token": "abc123token"})
    assert ok.status_code == 200


def test_agent_self_enrollment_flow():
    headers = _login_admin()
    token_resp = client.post("/agents/enrollment-tokens", headers=headers, json={"label": "test token"})
    assert token_resp.status_code == 201, token_resp.text
    enrollment_token = token_resp.json()["token"]

    enroll_resp = client.post("/agents/enroll/self", json={"token": enrollment_token, "name": "self-agent"})
    assert enroll_resp.status_code == 201, enroll_resp.text
    data = enroll_resp.json()
    assert "agent_id" in data and "token" in data

    cfg_resp = client.get(
        f"/agents/config/{data['agent_id']}",
        headers={"X-Agent-Token": data["token"]},
    )
    assert cfg_resp.status_code == 200, cfg_resp.text
