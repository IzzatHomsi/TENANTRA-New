# auth.py (dependencies) — updated for tenant context
from typing import Any, Dict, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class CurrentUser:
    """Minimal user context shared across routes.
    Includes id, username, roles, and tenant identifier for scoping.
    """
    def __init__(self, user_id: str, username: str, roles: Optional[List[str]] = None, tenant: Optional[str] = None):
        self.id = user_id
        self.username = username
        self.roles = roles or ["user"]
        # tenant string (could be tenant slug or id) used for scoping export roots
        self.tenant = (tenant or "default").strip()

def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """Decode JWT, validate expiry, and map common fields including tenant info."""
    payload: Optional[Dict[str, Any]] = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = str(payload.get("sub") or "").strip()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    username = str(payload.get("preferred_username") or payload.get("username") or f"user-{user_id}")
    raw_roles = payload.get("roles") or payload.get("role") or ["user"]
    if isinstance(raw_roles, str):
        roles = [raw_roles]
    else:
        roles = list(raw_roles)

    # Accept either 'tenant', 'tenant_id', or 'tid' claims; default to "default"
    tenant = str(payload.get("tenant") or payload.get("tenant_id") or payload.get("tid") or "default")

    return CurrentUser(user_id=user_id, username=username, roles=roles, tenant=tenant)
