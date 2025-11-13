# backend/app/core/security.py
# Security utilities: password hashing and JWT handling
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

# Password Hashing Context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_TEST_SECRET = "tenantra-test-secret"
_PLACEHOLDER_SECRET = "CHANGE_ME_IN_.ENV"
_TRUE_VALUES = {"1", "true", "yes", "on"}


def load_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "").strip()
    if secret and secret != _PLACEHOLDER_SECRET:
        return secret

    if os.getenv("PYTEST_CURRENT_TEST"):
        return os.getenv("TENANTRA_TEST_JWT_SECRET", _TEST_SECRET)

    bootstrap_flag = os.getenv("TENANTRA_TEST_BOOTSTRAP", "").strip().lower()
    if bootstrap_flag in _TRUE_VALUES:
        return os.getenv("TENANTRA_TEST_JWT_SECRET", _TEST_SECRET)

    raise RuntimeError(
        "JWT_SECRET must be set to a unique, non-default value (see docs for configuring environment secrets)."
    )


# JWT Configuration (env-backed; safe defaults for dev/test via helper above)
SECRET_KEY = load_jwt_secret()
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    if "jti" not in to_encode:
        to_encode["jti"] = uuid4().hex
    to_encode.update(
        {
            "exp": int(expire.timestamp()),
            "iat": now.timestamp(),
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def set_admin_password(new_password: str, username: str = "admin") -> None:
    """
    Helper for operational scripts to rotate the admin password safely.
    """
    if not new_password:
        raise ValueError("New password must not be empty.")

    from app.database import SessionLocal  # local import to avoid circular deps
    from app.models.user import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise RuntimeError(f"User '{username}' not found.")
        user.password_hash = get_password_hash(new_password)
        db.commit()
    finally:
        db.close()
