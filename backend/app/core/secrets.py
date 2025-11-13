import os
from typing import Optional

_ENC_KEY_CACHE: Optional[bytes] = None
_TRUE_VALUES = {"1", "true", "yes", "on"}


def _is_test_context() -> bool:
    return bool(
        os.getenv("PYTEST_CURRENT_TEST")
        or os.getenv("TESTING", "false").strip().lower() == "true"
        or os.getenv("TENANTRA_TEST_BOOTSTRAP", "").strip().lower() in _TRUE_VALUES
    )


def get_enc_key() -> bytes:
    """
    Retrieves the application's encryption key from the environment.

    Raises:
        RuntimeError: If the TENANTRA_ENC_KEY is not set in a non-test environment.
        ValueError: If the key is less than 32 bytes long.

    Returns:
        bytes: The encryption key.
    """
    global _ENC_KEY_CACHE
    if _ENC_KEY_CACHE:
        return _ENC_KEY_CACHE

    key = os.getenv("TENANTRA_ENC_KEY")

    if not key:
        if _is_test_context():
            # Use a non-secret, deterministic key for reproducible tests
            key = "test-key-for-pytest-runs-only-32-bytes"
        else:
            raise RuntimeError(
                "FATAL: TENANTRA_ENC_KEY environment variable not set. "
                "A 32-byte secret key is required for data encryption. "
                "Please generate one and set it."
            )

    if len(key.encode()) < 32:
        raise ValueError("TENANTRA_ENC_KEY must be at least 32 bytes long.")

    _ENC_KEY_CACHE = key.encode()
    return _ENC_KEY_CACHE
