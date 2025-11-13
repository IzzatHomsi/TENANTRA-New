from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from .helpers import ADMIN_USERNAME, ADMIN_PASSWORD

client = TestClient(app)


def _login(password: str = ADMIN_PASSWORD) -> tuple[str, dict[str, str]]:
    resp = client.post("/auth/login", data={"username": ADMIN_USERNAME, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return token, headers


def _restore_admin_password(password: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        assert user is not None
        user.password_hash = get_password_hash(password)
        db.add(user)
        db.commit()
    finally:
        db.close()


def test_forgot_password_and_reset_revokes_old_tokens():
    original_password = ADMIN_PASSWORD
    token, headers = _login()

    try:
        forgot = client.post("/auth/forgot-password", json={"username": ADMIN_USERNAME})
        assert forgot.status_code == 202, forgot.text
        reset_token = forgot.json().get("reset_token")
        assert reset_token, "Reset token should be included in test mode"

        new_password = "N3wSecurePass!"
        reset_resp = client.post("/auth/reset-password", json={"token": reset_token, "new_password": new_password})
        assert reset_resp.status_code == 200, reset_resp.text

        me_after_reset = client.get("/users/me", headers=headers)
        assert me_after_reset.status_code == 401, "Existing token should be revoked after password reset"

        login_new = client.post("/auth/login", data={"username": ADMIN_USERNAME, "password": new_password})
        assert login_new.status_code == 200, login_new.text
    finally:
        _restore_admin_password(original_password)


def test_logout_revokes_current_token():
    token, headers = _login()
    logout_resp = client.post("/auth/logout", headers=headers)
    assert logout_resp.status_code == 204

    me_resp = client.get("/users/me", headers=headers)
    assert me_resp.status_code == 401
