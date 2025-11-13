import os

ADMIN_USERNAME = os.getenv("TENANTRA_TEST_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("TENANTRA_TEST_ADMIN_PASSWORD")

if not ADMIN_PASSWORD:
    raise RuntimeError("TENANTRA_TEST_ADMIN_PASSWORD must be set before running backend tests.")
