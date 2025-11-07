from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


client = TestClient(app)
DEFAULT_PASSWORD = "Admin@1234"


def _login(password: str = DEFAULT_PASSWORD) -> str:
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": password},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    return body["access_token"]


@pytest.fixture(autouse=True)
def _reset_admin_state():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    assert admin is not None, "Admin user must exist for profile tests"

    original_email = admin.email
    original_hash = admin.password_hash

    admin.password_hash = get_password_hash(DEFAULT_PASSWORD)
    admin.email = original_email or "admin@example.com"
    db.commit()

    try:
        yield
    finally:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            admin.email = original_email
            admin.password_hash = original_hash
            db.commit()
        db.close()


def test_get_users_me():
    token = _login()
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"


def test_update_email_only():
    token = _login()
    new_email = "admin_updated@tenantra.local"
    response = client.put(
        "/users/me",
        json={"new_email": new_email},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == new_email


def test_change_password_success():
    token = _login()
    new_password = "Admin@12345"
    response = client.put(
        "/users/me",
        json={
            "current_password": DEFAULT_PASSWORD,
            "new_password": new_password,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    new_token = _login(password=new_password)
    assert new_token
