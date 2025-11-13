from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.agent import Agent
from app.models.user import User
from .helpers import ADMIN_USERNAME, ADMIN_PASSWORD


client = TestClient(app)


def _login_admin() -> str:
    resp = client.post("/auth/login", data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _ensure_agent(tenant_id: int) -> int:
    db = SessionLocal()
    try:
        agent = Agent(tenant_id=tenant_id, name="agent-reg")
        db.add(agent); db.commit(); db.refresh(agent)
        return agent.id
    finally:
        db.close()


def test_registry_ingest_and_drift_summary():
    token = _login_admin()
    db = SessionLocal();
    try:
        admin: User = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        tid = admin.tenant_id or 1
    finally:
        db.close()
    agent_id = _ensure_agent(tid)

    headers = {"Authorization": f"Bearer {token}"}
    hive = "HKLM"
    key_path = r"SOFTWARE\\Example"

    # initial value
    payload = [
        {"agent_id": agent_id, "hive": hive, "key_path": key_path, "value_name": "Path", "value_data": "C:/A", "value_type": "REG_SZ", "collected_at": datetime.utcnow().isoformat()}
    ]
    r = client.post("/integrity/registry", json=payload, headers=headers)
    assert r.status_code == 200

    # modify value
    payload[0]["value_data"] = "C:/B"
    r = client.post("/integrity/registry", json=payload, headers=headers)
    assert r.status_code == 200

    # drift summary should reflect modifications/new
    r = client.get(f"/integrity/registry/drift?agent_id={agent_id}&hive={hive}", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get("modified_entries"), list)
