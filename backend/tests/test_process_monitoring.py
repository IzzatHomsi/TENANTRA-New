from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base_class import Base
from app.database import get_db
from app.core.auth import get_current_user
from app.models.tenant import Tenant
from app.models.agent import Agent


def setup_module(module):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_current_user():
        return SimpleNamespace(id=1, tenant_id=1, role="admin")

    module.engine = engine
    module.TestingSessionLocal = TestingSessionLocal

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    db = TestingSessionLocal()
    tenant = Tenant(id=1, name="Test", slug="test", is_active=True, storage_quota_gb=10)
    agent = Agent(id=1, tenant_id=1, name="Agent One", status="active")
    db.add(tenant)
    db.add(agent)
    db.commit()
    db.close()


def teardown_module(module):
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)
    Base.metadata.drop_all(bind=module.engine)


def test_process_report_drift_detection():
    client = TestClient(app)

    baseline_payload = {
        "agent_id": 1,
        "processes": [
            {
                "process_name": "sshd",
                "executable_path": "/usr/sbin/sshd",
                "expected_hash": "abc",
                "expected_user": "root",
                "is_critical": True,
            }
        ],
    }
    resp = client.post("/processes/baseline", json=baseline_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["entries"][0]["process_name"] == "sshd"

    report_payload = {
        "agent_id": 1,
        "full_sync": True,
        "processes": [
            {
                "pid": 1001,
                "process_name": "sshd",
                "executable_path": "/usr/sbin/sshd",
                "username": "root",
                "hash": "abc",
                "command_line": "sshd -D",
            }
        ],
    }
    first_report = client.post("/processes/report", json=report_payload)
    assert first_report.status_code == 200
    body = first_report.json()
    assert body["drift"]["events"] == []

    # Missing critical process should trigger drift
    second_report_payload = {
        "agent_id": 1,
        "full_sync": True,
        "processes": [],
    }
    second_report = client.post("/processes/report", json=second_report_payload)
    assert second_report.status_code == 200
    drift = second_report.json()["drift"]["events"]
    assert drift and drift[0]["change_type"] == "missing_critical"
    assert drift[0]["process_name"] == "sshd"

