from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _login_admin() -> str:
    r = client.post("/auth/login", data={"username": "admin", "password": "Admin@1234"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_service_baseline_roundtrip():
    token = _login_admin()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "agent_id": None,
        "entries": [
            {"name": "svcA", "expected_status": "running", "expected_start_mode": "auto", "is_critical": True},
            {"name": "svcB", "expected_status": "stopped"}
        ]
    }
    r = client.post("/integrity/services/baseline", json=payload, headers=headers)
    assert r.status_code == 200

    r = client.get("/integrity/services/baseline", headers=headers)
    assert r.status_code == 200
    rows = r.json()
    assert any(e.get("name") == "svcA" for e in rows)

