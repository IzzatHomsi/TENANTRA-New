from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _has_path(paths, p: str) -> bool:
    return p in paths or f"/api{p}" in paths


def test_openapi_includes_notification_routes():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    paths = resp.json().get("paths", {})
    assert _has_path(paths, "/notification-history"), "notification history path missing from OpenAPI"
    assert _has_path(paths, "/notifications/settings"), "notification settings path missing from OpenAPI"

