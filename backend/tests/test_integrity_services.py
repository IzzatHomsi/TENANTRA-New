from datetime import datetime, timedelta
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
        agent = Agent(tenant_id=tenant_id, name="agent-1")
        db.add(agent); db.commit(); db.refresh(agent)
        return agent.id
    finally:
        db.close()


def test_service_ingest_and_event():
    token = _login_admin()
    # fetch admin for tenant id
    db = SessionLocal();
    try:
        admin: User = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        tid = admin.tenant_id or 1
    finally:
        db.close()
    agent_id = _ensure_agent(tid)

    headers = {"Authorization": f"Bearer {token}"}

    # initial snapshot
    payload = [
        {
            "agent_id": agent_id,
            "name": "svcA",
            "display_name": "Service A",
            "status": "stopped",
            "start_mode": "disabled",
            "run_account": "LocalSystem",
            "binary_path": None,
            "hash": None,
            "collected_at": datetime.utcnow().isoformat(),
        }
    ]
    r = client.post("/integrity/services", json=payload, headers=headers)
    assert r.status_code == 200

    # change snapshot
    payload[0]["status"] = "running"
    payload[0]["start_mode"] = "auto"
    r = client.post("/integrity/services", json=payload, headers=headers)
    assert r.status_code == 200

    # events should include a service_change
    r = client.get("/integrity/events", headers=headers)
    assert r.status_code == 200
    events = r.json()
    assert any(evt.get("event_type") == "service_change" for evt in events)
