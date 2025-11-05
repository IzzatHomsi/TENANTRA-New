# Filename: backend/tests/test_user_profile.py

import requests

BASE_URL = "http://localhost:5000"

# Helper function to get a valid token
def get_token():
    """Authenticate as the default admin user and return a JWT token."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "Admin@1234"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

def test_get_users_me():
    token = get_token()
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "username" in response.json()
    print("✅ GET /users/me passed.")

def test_update_email_only():
    token = get_token()
    new_email = "admin_updated@tenantra.local"
    response = requests.put(
        f"{BASE_URL}/users/me",
        json={"new_email": new_email},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == new_email
    print("✅ PUT /users/me (email only) passed.")

def test_change_password_success():
    token = get_token()
    response = requests.put(
        f"{BASE_URL}/users/me",
        json={
            "new_password": "Admin@12345",
            "current_password": "Admin@1234"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    print("✅ PUT /users/me (change password) passed.")
