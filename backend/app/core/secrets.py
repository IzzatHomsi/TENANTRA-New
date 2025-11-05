import os
import secrets
from typing import Optional

_JWT_SECRET: Optional[str] = None
_ENC_KEY_CACHE: Optional[bytes] = None
_DEFAULT_ENC_KEY = "tenantra-dev-enc-key-change-me"

def get_jwt_secret() -> str:
    global _JWT_SECRET
    if _JWT_SECRET:
        return _JWT_SECRET
    secret = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
    _JWT_SECRET = secret
    return _JWT_SECRET

def get_enc_key() -> bytes:
    global _ENC_KEY_CACHE
    if _ENC_KEY_CACHE:
        return _ENC_KEY_CACHE
    key = os.getenv("TENANTRA_ENC_KEY")
    if not key:
        key = os.getenv("JWT_SECRET") or _DEFAULT_ENC_KEY
    if isinstance(key, bytes):
        _ENC_KEY_CACHE = key
    else:
        _ENC_KEY_CACHE = key.encode()
    return _ENC_KEY_CACHE
