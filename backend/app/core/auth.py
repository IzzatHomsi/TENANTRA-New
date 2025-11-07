"""Authentication helpers for FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import security as security_utils
from app.database import get_db
from app.models.user import User

# ---------------------------------------------------------------------------
# JWT configuration (delegated to security module)
# ---------------------------------------------------------------------------
SECRET_KEY = security_utils.SECRET_KEY
ALGORITHM = security_utils.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = security_utils.ACCESS_TOKEN_EXPIRE_MINUTES
pwd_context = security_utils.pwd_context
verify_password = security_utils.verify_password
get_password_hash = security_utils.get_password_hash
create_access_token = security_utils.create_access_token
decode_access_token = security_utils.decode_access_token

# OAuth2 scheme used by classic dependencies (extracts Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------

def _resolve_user_from_token(token: str, db: Session) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    return _resolve_user_from_token(token, db)

_DEF_ADMIN_ROLES = {"admin", "administrator", "super_admin", "system_admin"}
_SETTINGS_READ_ROLES = _DEF_ADMIN_ROLES | {"auditor", "audit", "read_only_admin", "msp_admin"}

def get_admin_user(
    db: Session = Depends(get_db),
    authorization: str = Header(..., alias="Authorization"),
) -> User:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = _resolve_user_from_token(token, db)
    role = (getattr(user, "role", "") or "").strip().lower()
    if role not in _DEF_ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


def get_settings_user(
    db: Session = Depends(get_db),
    authorization: str = Header(..., alias="Authorization"),
) -> User:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = _resolve_user_from_token(token, db)
    role = (getattr(user, "role", "") or "").strip().lower()
    if role not in _SETTINGS_READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Settings permission required")
    return user
