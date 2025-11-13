import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
ADMIN_USERNAME = os.getenv("TENANTRA_TEST_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("TENANTRA_TEST_ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    raise RuntimeError("TENANTRA_TEST_ADMIN_PASSWORD must be set before running test_auth.py")

def test_admin_login():
    print("[TEST] Checking /auth/login with provided admin credentials")
    response = requests.post(f"{BASE_URL}/auth/login",
                             data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        response.raise_for_status()
        print("[OK] Login successful")
        print("Response:", response.json())
    except Exception as e:
        print("[ERROR] Login failed:", response.text)

if __name__ == "__main__":
    test_admin_login()
