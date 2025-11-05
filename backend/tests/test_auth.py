import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

def test_admin_login():
    print("[TEST] Checking /auth/login with admin/admin123")
    response = requests.post(f"{BASE_URL}/auth/login",
                             data={"username": "admin", "password": "Admin@1234"},
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        response.raise_for_status()
        print("[OK] Login successful")
        print("Response:", response.json())
    except Exception as e:
        print("[ERROR] Login failed:", response.text)

if __name__ == "__main__":
    test_admin_login()
