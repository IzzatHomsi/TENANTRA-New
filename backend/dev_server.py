"""
Development helper to run the API with a local SQLite DB and test bootstrap.

This avoids relying on parent process environment inheritance on Windows.
"""
from __future__ import annotations

import os
import pathlib
import uvicorn


def main() -> None:
    here = pathlib.Path(__file__).resolve().parent
    os.chdir(here)
    os.environ.setdefault("DB_URL", "sqlite:///./test_api.db")
    os.environ.setdefault("TENANTRA_TEST_BOOTSTRAP", "1")
    # Keep background workers off during tests/dev runs unless explicitly enabled
    os.environ.setdefault("TENANTRA_ENABLE_NOTIFICATIONS_WORKER", "0")
    os.environ.setdefault("TENANTRA_ENABLE_MODULE_SCHEDULER", "0")
    # Loosen rate-limit for critical test paths to avoid flakiness
    os.environ.setdefault(
        "RATE_LIMIT_SKIP",
        ",".join([
            "/auth", "/api/auth", "/users/me", "/api/users/me",
            "/health", "/metrics", "/openapi.json",
        ]),
    )
    # Deterministic JWT secret in dev to keep tokens valid across processes
    os.environ.setdefault("JWT_SECRET", "dev-local-fixed-secret-change-in-prod")
    uvicorn.run("app.main:app", host="127.0.0.1", port=5000, log_level="warning")


if __name__ == "__main__":
    main()
