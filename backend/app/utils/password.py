import re
from datetime import datetime, timedelta
from passlib.context import CryptContext


class PasswordValidationError(Exception):
    pass


def validate_password_strength(password: str):
    """Raise an exception if the password is too weak."""
    if len(password) < 8:
        raise PasswordValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise PasswordValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise PasswordValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise PasswordValidationError("Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise PasswordValidationError("Password must contain at least one special character.")


def compute_expiry(days_valid=90):
    """Return a datetime that is X days in the future (used for password expiry)."""
    return datetime.utcnow() + timedelta(days=days_valid)


# ✅ Bcrypt context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)
