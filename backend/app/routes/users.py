# backend/app/routes/users.py
# ------------------------------------------------------------
# Tenantra — Users Routes (S‑R1 Step 1)
# Purpose: expose PUT /users/me for self‑service profile updates (email/password),
#          ensuring the router is actually included by main.py.
# ------------------------------------------------------------
# SECURITY SUMMARY (for non-devs):
# - Only an authenticated user can call PUT /users/me.
# - We validate inputs strictly; we never return or log passwords.
# - Password updates require the current password and store a bcrypt hash.
# ------------------------------------------------------------

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import verify_password, get_password_hash, decode_access_token

router = APIRouter(prefix="/users", tags=["users"])

# Reuse the same OAuth2 scheme defined in auth.py; we recreate it here to keep this file independent.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _require_current_user(token: str, db: Session) -> User:
    """
    Resolve the current user from a bearer token. Raise 401/404 on problems.
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/me")
def update_self(
    # Authorization bearer token is required.
    token: str = Depends(oauth2_scheme),
    # Align payload with tests: "new_email" and optional password change fields
    new_email: Optional[str] = Body(default=None, embed=True),
    current_password: Optional[str] = Body(default=None, embed=True),
    new_password: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
):
    """
    Update current user's email and/or password.
    Mirrors the contract used by tests: accepts 'new_email' and returns the updated user fields at top level.
    """
    # Resolve the current user from the token.
    user = _require_current_user(token, db)

    changed = False

    # Update email if provided
    if new_email is not None:
        if "@" not in new_email or "." not in new_email:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email format")
        user.email = new_email
        changed = True

    # Update password if provided (requires current password)
    if (current_password is not None) or (new_password is not None):
        if not current_password or not new_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Both current_password and new_password are required")
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid current password")
        user.password_hash = get_password_hash(new_password)
        changed = True

    if changed:
        db.add(user)
        db.commit()
        db.refresh(user)

    # Return unified top-level user data like users_me.py
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }
