from typing import Iterable, Optional, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

# Role constants
ROLE_ADMIN = "admin"
ROLE_STANDARD = "standard_user"
ROLE_SUPER = "super_admin"  # if you later introduce it

def require_roles(*roles: str) -> Callable[[User], User]:
    """Dependency factory: ensure current user has one of the roles."""
    def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return current_user
    return _dep

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != ROLE_ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user

def require_tenant_scope(
    user_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Ensure the acting user shares the same tenant as the target user."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    actor_tenant = getattr(current_user, "tenant_id", None)
    target_tenant = getattr(target, "tenant_id", None)
    if actor_tenant is None:
        return
    if target_tenant != actor_tenant:
        raise HTTPException(status_code=403, detail="Tenant mismatch")
