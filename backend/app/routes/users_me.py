# Filename: backend/app/routes/users_me.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.models.user import User
from app.core.security import decode_access_token, verify_password, get_password_hash
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Define a Pydantic schema for update payload
class UserUpdateRequest(BaseModel):
    new_email: Optional[str] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None

@router.get("/users/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    ✅ Fetch current authenticated user's profile
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }

@router.put("/users/me")
def update_current_user(update_data: UserUpdateRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    ✅ Update current user's email and/or password
    - Requires JWT token
    - Password update requires current password confirmation
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update email if provided
    if update_data.new_email:
        user.email = update_data.new_email

    # Handle password update with confirmation
    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(status_code=400, detail="Current password required to change password")

        if not verify_password(update_data.current_password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid current password")

        user.password_hash = get_password_hash(update_data.new_password)

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }
