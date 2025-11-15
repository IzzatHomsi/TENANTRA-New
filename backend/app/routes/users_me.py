# Filename: backend/app/routes/users_me.py

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.security import get_password_hash, verify_password
from app.database import get_db
from app.models.user import User

router = APIRouter()


class UserUpdateRequest(BaseModel):
    new_email: Optional[str] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None


@router.get("/users/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    ✅ Fetch current authenticated user's profile via the shared auth dependency
    so revoked tokens (logout/reset) are respected everywhere.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "email_verified": bool(getattr(current_user, "email_verified_at", None)),
    }


@router.put("/users/me")
def update_current_user(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ Update current user's email and/or password
    - Requires JWT token resolved through get_current_user (includes revocation checks)
    - Password update requires current password confirmation
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if update_data.new_email:
        user.email = update_data.new_email

    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password required to change password",
            )
        if not verify_password(update_data.current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid current password")
        user.password_hash = get_password_hash(update_data.new_password)

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "email_verified": bool(getattr(user, "email_verified_at", None)),
    }
