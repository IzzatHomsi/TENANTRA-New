from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.app_setting import AppSetting
from app.models.audit_log import AuditLog
from app.routes import grafana_proxy as grafana_proxy_module
from app.core.crypto import encrypt_data
from app.core.secrets import get_enc_key
from .helpers import ADMIN_USERNAME, ADMIN_PASSWORD


client = TestClient(app)


def _login_admin() -> dict[str, str]:
    response = client.post(
        "/auth/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _ensure_setting(key: str, value):
    db = SessionLocal()
    try:
        row = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id.is_(None), AppSetting.key == key)
            .one_or_none()
        )
        previous = row.value if row else None
        if row:
            row.value = value
        else:
            db.add(AppSetting(tenant_id=None, key=key, value=value))
        db.commit()
        return previous
    finally:
        db.close()


def _delete_setting(key: str) -> None:
    db = SessionLocal()
    try:
        row = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id.is_(None), AppSetting.key == key)
            .first()
        )
        if row:
            db.delete(row)
            db.commit()
    finally:
        db.close()


def _restore_setting(key: str, previous):
    if previous is None:
        _delete_setting(key)
    else:
        _ensure_setting(key, previous)


@patch("app.routes.grafana_proxy.httpx.AsyncClient.request", new_callable=AsyncMock)
def test_grafana_proxy_injects_headers(mock_request: AsyncMock):
    headers = _login_admin()
    previous_url = _ensure_setting("grafana.url", "http://grafana:3000")
    try:
        response = httpx.Response(
            status_code=200,
            request=httpx.Request("GET", "http://grafana:3000/api/search"),
            content=b"{}",
        )
        mock_request.return_value = response

        resp = client.get("/grafana/api/search", headers=headers)
        assert resp.status_code == 200
        assert mock_request.call_count == 1
        _, kwargs = mock_request.call_args
        forwarded_headers = kwargs["headers"]
        assert forwarded_headers["X-Requested-By"] == "tenantra-backend"
        assert forwarded_headers["X-User-Id"]
        assert forwarded_headers["X-Tenant-Id"]
    finally:
        _restore_setting("grafana.url", previous_url)


@patch("app.routes.grafana_proxy.httpx.AsyncClient.request", new_callable=AsyncMock)
def test_grafana_proxy_body_limit_override(mock_request: AsyncMock):
    headers = _login_admin()
    previous_url = _ensure_setting("grafana.url", "http://grafana:3000")
    previous_limit = _ensure_setting("grafana.proxy.max_body_bytes", 8)
    try:
        resp = client.post("/grafana/api/ingest", headers=headers, content="0123456789")
        assert resp.status_code == 413
        mock_request.assert_not_called()
    finally:
        _restore_setting("grafana.proxy.max_body_bytes", previous_limit)
        _restore_setting("grafana.url", previous_url)


@patch("app.routes.grafana_proxy.httpx.AsyncClient.request", new_callable=AsyncMock)
def test_grafana_proxy_rate_limit_enforced(mock_request: AsyncMock):
    headers = _login_admin()
    previous_url = _ensure_setting("grafana.url", "http://grafana:3000")
    previous_rate = _ensure_setting("grafana.proxy.max_requests_per_minute", 1)
    grafana_proxy_module._RATE_BUCKETS.clear()

    response = httpx.Response(
        status_code=200,
        request=httpx.Request("GET", "http://grafana:3000/api/search"),
        content=b"{}",
    )
    mock_request.return_value = response
    try:
        first = client.get("/grafana/api/search", headers=headers)
        assert first.status_code == 200
        second = client.get("/grafana/api/search", headers=headers)
        assert second.status_code == 429

        db = SessionLocal()
        try:
            audit = (
                db.query(AuditLog)
                .filter(AuditLog.action == "grafana.proxy")
                .order_by(AuditLog.id.desc())
                .first()
            )
            assert audit is not None
            assert "rate-limit" in (audit.details or "")
        finally:
            db.close()
    finally:
        _restore_setting("grafana.proxy.max_requests_per_minute", previous_rate)
        _restore_setting("grafana.url", previous_url)


@patch("app.routes.grafana_proxy.httpx.AsyncClient.request", new_callable=AsyncMock)
def test_grafana_proxy_uses_stored_credentials(mock_request: AsyncMock):
    headers = _login_admin()
    previous_url = _ensure_setting("grafana.url", "http://grafana:3000")
    previous_user = _ensure_setting("grafana.basic.username", "svc-grafana")
    ciphertext = encrypt_data("Sup3rSecret!", get_enc_key())
    previous_password = _ensure_setting("grafana.basic.password", {"ciphertext": ciphertext, "set": True})
    response = httpx.Response(
        status_code=200,
        request=httpx.Request("GET", "http://grafana:3000/api/search"),
        content=b"{}",
    )
    mock_request.return_value = response
    try:
        resp = client.get("/grafana/api/search", headers=headers)
        assert resp.status_code == 200
        _, kwargs = mock_request.call_args
        auth_header = kwargs["headers"].get("Authorization")
        assert auth_header and auth_header.startswith("Basic ")
    finally:
        _restore_setting("grafana.basic.password", previous_password)
        _restore_setting("grafana.basic.username", previous_user)
        _restore_setting("grafana.url", previous_url)
