"""Admin-only user management endpoints."""

from __future__ import annotations

import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
import os
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator

from app.core.security import decode_access_token, get_password_hash
from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ADMIN_ROLES = {"admin", "administrator", "super_admin", "system_admin"}
SUPER_ADMIN_ROLES = {"super_admin", "system_admin"}


class UserAdminOut(BaseModel):
    """Shape returned to clients when listing/creating users."""

    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    role: Optional[str] = None
    tenant_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserCreateIn(BaseModel):
    """Payload when the admin creates a new user."""

    username: str
    password: str
    email: Optional[EmailStr] = None
    role: str = "standard_user"
    tenant_id: Optional[int] = None

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")
        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError("Password must contain a special character")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class UserUpdateIn(BaseModel):
    """Payload used when updating an existing user."""

    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    tenant_id: Optional[int] = None

    @field_validator("password")
    def validate_optional_password(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        if (
            len(value) < 8
            or not re.search(r"[a-z]", value)
            or not re.search(r"[A-Z]", value)
            or not re.search(r"\d", value)
            or not re.search(r"[^A-Za-z0-9]", value)
        ):
            raise ValueError(
                "Password must be at least 8 characters and include upper, lower, digit, and special character"
            )
        return value


def get_current_user(db: Session, token: str) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        ) from exc
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def require_admin(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    current = get_current_user(db, token)
    role = (getattr(current, "role", None) or "").lower()
    if role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current


def _is_super_admin(user: User) -> bool:
    role = (getattr(user, "role", None) or "").strip().lower()
    return role in SUPER_ADMIN_ROLES


def _resolve_tenant_scope(admin: User, requested_tenant_id: Optional[int]) -> Optional[int]:
    """
    Determine which tenant_id should be used for an operation initiated by `admin`.
    Standard admins are forced to their own tenant; super-admins may optionally
    target a specific tenant (but must specify one if they have none assigned).
    """
    if not _is_super_admin(admin):
        return admin.tenant_id

    # Super-admins can target an explicit tenant_id when provided,
    # otherwise default to their assigned tenant (which may be None).
    if requested_tenant_id is not None:
        return requested_tenant_id
    return admin.tenant_id


def _ensure_valid_tenant(db: Session, tenant_id: Optional[int]) -> Optional[int]:
    if tenant_id is None:
        return None
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return tenant_id


def _enforce_same_tenant(admin: User, target: User) -> None:
    if _is_super_admin(admin):
        return
    if admin.tenant_id != target.tenant_id:
        # Return 404 to avoid leaking the existence of users in other tenants.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get("/users", response_model=List[UserAdminOut])
def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> List[UserAdminOut]:
    env = (os.getenv("TENANTRA_ENV", "") or os.getenv("ENV", "")).strip().lower()
    q = db.query(User)
    if not _is_super_admin(admin):
        q = q.filter(User.tenant_id == admin.tenant_id)
    if env in {"development", "dev", "local"}:
        # In development, hide inactive users (soft-deleted ones)
        q = q.filter(User.is_active == True)
    users = q.order_by(User.id.asc()).all()
    return [UserAdminOut.model_validate(u) for u in users]


@router.post("/users", response_model=UserAdminOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreateIn,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserAdminOut:
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    if payload.email and db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    tenant_id = _resolve_tenant_scope(admin, payload.tenant_id)
    tenant_id = _ensure_valid_tenant(db, tenant_id)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a user without an associated tenant",
        )

    password_hash = get_password_hash(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        is_active=True,
        role=payload.role,
        password_hash=password_hash,
        tenant_id=tenant_id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserAdminOut.model_validate(user)


@router.put("/users/{user_id}", response_model=UserAdminOut)
def update_user(
    user_id: int,
    payload: UserUpdateIn,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserAdminOut:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    _enforce_same_tenant(admin, user)

    if payload.email is not None and payload.email != user.email:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        user.email = payload.email

    if payload.role is not None:
        user.role = payload.role

    if payload.is_active is not None:
        user.is_active = payload.is_active

    if payload.password:
        user.password_hash = get_password_hash(payload.password)

    if payload.tenant_id is not None:
        if not _is_super_admin(admin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant reassignment not permitted")
        tenant_id = _ensure_valid_tenant(db, payload.tenant_id)
        user.tenant_id = tenant_id

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserAdminOut.model_validate(user)


@router.delete("/users/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Administrators cannot delete themselves")

    _enforce_same_tenant(admin, user)

    try:
        db.delete(user)
        db.commit()
        return {"deleted": True, "user_id": user_id}
    except IntegrityError:
        db.rollback()
        env = (os.getenv("TENANTRA_ENV", "") or os.getenv("ENV", "")).strip().lower()
        if env in {"development", "dev", "local"}:
            try:
                # Soft-delete in development: mark inactive and rename for clarity
                user.is_active = False
                if user.username and not user.username.startswith("deleted:"):
                    user.username = f"deleted:{user.username}"
                db.add(user)
                db.commit()
                return {"deleted": True, "user_id": user_id, "soft": True}
            except IntegrityError:
                db.rollback()
        # If user is referenced (e.g., created_by relationships), return 409 instead of 500
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted because it is referenced by other records",
        )
