"""Helpers for resolving the initial admin password used during bootstrap/seed."""

from __future__ import annotations

import os
import secrets
from typing import Optional

_TRUE_VALUES = {"1", "true", "yes", "on"}
_TEST_PASSWORD_CACHE: Optional[str] = None


def _is_test_mode() -> bool:
    """Return True when running under pytest/dev bootstrap."""
    return bool(
        os.getenv("PYTEST_CURRENT_TEST")
        or os.getenv("TENANTRA_TEST_BOOTSTRAP", "").strip().lower() in _TRUE_VALUES
        or os.getenv("TESTING", "").strip().lower() == "true"
    )


def _resolve_test_password() -> str:
    """Resolve or generate a deterministic password for test contexts."""
    global _TEST_PASSWORD_CACHE
    if _TEST_PASSWORD_CACHE:
        return _TEST_PASSWORD_CACHE

    existing = (os.getenv("TENANTRA_TEST_ADMIN_PASSWORD") or "").strip()
    if not existing:
        existing = secrets.token_urlsafe(16)
        # Ensure child processes reuse the same secret
        os.environ["TENANTRA_TEST_ADMIN_PASSWORD"] = existing

    _TEST_PASSWORD_CACHE = existing
    return _TEST_PASSWORD_CACHE


def resolve_admin_password(env_var: str = "TENANTRA_ADMIN_PASSWORD") -> str:
    """
    Resolve the admin password that seed/bootstrap flows must use.

    In production-like environments the caller must provide TENANTRA_ADMIN_PASSWORD.
    In test/bootstrap contexts we automatically fall back to a deterministic
    TENANTRA_TEST_ADMIN_PASSWORD (generating one if necessary).
    """
    if _is_test_mode():
        test_password = (os.getenv("TENANTRA_TEST_ADMIN_PASSWORD") or _resolve_test_password()).strip()
        if not test_password:
            test_password = _resolve_test_password()
        os.environ[env_var] = test_password
        return test_password

    password = (os.getenv(env_var) or "").strip()
    if password:
        return password

    raise RuntimeError(
        f"{env_var} must be set before bootstrapping Tenantra credentials. "
        "See .env.example for the required variables."
    )
