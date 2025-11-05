import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

client = TestClient(app)

def create_test_user(username, password, role):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username, email=f"{username}@test.com",
            password_hash=get_password_hash(password), role=role, is_active=True, tenant_id=1
        )
        db.add(user)
        db.commit()
    db.close()
    return user

@pytest.fixture(scope="module")
def admin_token():
    create_test_user("admin_test", "admin123", "admin")
    db = SessionLocal()
    user = db.query(User).filter(User.username == "admin_test").first()
    token = create_access_token({"sub": str(user.id)})
    db.close()
    return token

@pytest.fixture(scope="module")
def user_token():
    create_test_user("user_test", "user123", "standard_user")
    db = SessionLocal()
    user = db.query(User).filter(User.username == "user_test").first()
    token = create_access_token({"sub": str(user.id)})
    db.close()
    return token

def test_admin_can_access_users(admin_token):
    response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_standard_user_cannot_access_users(user_token):
    response = client.get("/users", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert "Admin access required" in response.text
