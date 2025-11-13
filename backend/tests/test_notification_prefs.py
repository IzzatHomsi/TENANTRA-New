from fastapi.testclient import TestClient

from app.main import app
from .helpers import ADMIN_USERNAME, ADMIN_PASSWORD

client = TestClient(app)


def _login() -> dict[str, str]:
    resp = client.post(
        "/auth/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_notification_prefs_round_trip():
    headers = _login()

    resp = client.get("/notification-prefs", headers=headers)
    assert resp.status_code == 200

    payload = {
        "channels": {"email": True, "webhook": False},
        "events": {"scan_failed": True, "agent_offline": False},
        "digest": "immediate",
    }
    put_resp = client.put("/notification-prefs", headers=headers, json=payload)
    assert put_resp.status_code == 200, put_resp.text
    body = put_resp.json()
    assert body["channels"]["email"] is True
    assert body["events"]["scan_failed"] is True

    resp_again = client.get("/notification-prefs", headers=headers)
    assert resp_again.status_code == 200
    assert resp_again.json()["channels"]["email"] is True
