from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.scheduled_scan import ScheduledScan

client = TestClient(app)


def _login_admin() -> str:
    resp = client.post("/auth/login", data={"username": "admin", "password": "Admin@1234"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token
    return token


def test_create_and_delete_schedule():
    token = _login_admin()

    # pick an existing module id via API
    modules = client.get("/modules/", headers={"Authorization": f"Bearer {token}"})
    assert modules.status_code == 200
    module_list = modules.json()
    assert module_list
    module_id = module_list[0]["id"]

    payload = {"module_id": module_id, "cron_expr": "*/30 * * * *"}
    create_resp = client.post("/schedules", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert create_resp.status_code == 201
    schedule_body = create_resp.json()
    schedule_id = schedule_body["id"]
    assert schedule_body["module_id"] == module_id

    list_resp = client.get(f"/schedules?module_id={module_id}", headers={"Authorization": f"Bearer {token}"})
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert any(item["id"] == schedule_id for item in items)

    delete_resp = client.delete(f"/schedules/{schedule_id}", headers={"Authorization": f"Bearer {token}"})
    assert delete_resp.status_code == 204

    cleanup = SessionLocal()
    try:
        assert cleanup.query(ScheduledScan).filter(ScheduledScan.id == schedule_id).first() is None
    finally:
        cleanup.close()
