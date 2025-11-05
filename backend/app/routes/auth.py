# backend/app/routes/auth.py
# Authentication routes: robust /auth/login (form or JSON) and /auth/me

from typing import Optional  # import Optional for fields that may be None
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response  # FastAPI primitives
from fastapi.security import OAuth2PasswordBearer  # OAuth2 token extractor from Authorization header
from sqlalchemy.orm import Session  # SQLAlchemy session type for DB work
from pydantic import BaseModel  # Pydantic models for request/response typing

from app.database import get_db  # dependency that yields a DB session
from app.models.tenant_cors_origin import TenantCORSOrigin
from app.models.tenant import Tenant
import os
from app.models.user import User  # ORM model for users table
from app.core.security import verify_password, create_access_token, decode_access_token  # crypto helpers

# Create a router; app mounts this under /api in main.py
router = APIRouter()

# Extract Bearer tokens sent to protected endpoints (e.g., /auth/me)
# tokenUrl informs OpenAPI docs where tokens are obtained.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic models (request/response) ----------

class LoginJSON(BaseModel):
    """Request body when client submits JSON instead of form."""
    username: str  # login name
    password: str  # plain password; verified against hash

class UserOut(BaseModel):
    """Unified shape the frontend expects from /auth/me (and we also reuse at login)."""
    id: int                   # user primary key
    username: str             # username
    email: Optional[str] = None  # email (may be None for some seeds)
    is_active: bool           # active flag
    role: Optional[str] = None  # <-- ROLE INCLUDED so RBAC gating works client-side

    class Config:
        # If later you return ORM objects directly, this lets Pydantic read attributes.
        from_attributes = True

class TokenOut(BaseModel):
    """Response shape for issuing access tokens."""
    access_token: str         # JWT
    token_type: str           # usually 'bearer'
    # We include the user profile to let the frontend gate immediately after login.
    user: UserOut             # embedded minimal user snapshot (includes role)

# ---------- Routes ----------

@router.post("/auth/login", response_model=TokenOut)
async def login(
    request: Request,                         # raw request (to inspect content-type / JSON body)
    username: Optional[str] = Form(None),     # OAuth2 form field: username
    password: Optional[str] = Form(None),     # OAuth2 form field: password
    db: Session = Depends(get_db),            # DB session injection
):
    """
    Accepts either:
    - Form: application/x-www-form-urlencoded (username, password)
    - JSON: application/json { "username": "...", "password": "..." }
    Returns: TokenOut { access_token, token_type, user{...} }
    """
    # If form payload missing, try JSON body gracefully
    if not username or not password:
        # Check if client sent JSON and parse it
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                data = await request.json()   # parse JSON body
                model = LoginJSON(**data)     # validate via Pydantic
                username, password = model.username, model.password  # extract fields
            except Exception as e:
                # Bad JSON or missing fields: tell client exactly what is wrong
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid JSON payload: {e}",
                )
        else:
            # Neither form nor valid JSON provided
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Missing 'username' and 'password' (form or JSON).",
            )

    # Lookup user by username (case-sensitive; align with your seeds)
    user = db.query(User).filter(User.username == username).first()  # fetch user record

    # If no match or password mismatch, deny with 401 (do not reveal which part failed)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create a short-lived access token using user id as subject (sub)
    access_token = create_access_token(data={"sub": str(user.id)})

    # Return token + minimal user profile (includes role for immediate RBAC on the client)
    return TokenOut(
        access_token=access_token,
        token_type="bearer",  # nosec B106: this is a token type label, not a secret
        user=UserOut(
            id=user.id,
            username=user.username,
            email=getattr(user, "email", None),
            is_active=bool(getattr(user, "is_active", True)),
            role=getattr(user, "role", None),
        ),
    )


def _parse_env_allowed_origins() -> set[str]:
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return set(parts)


@router.options("/auth/login")
def login_preflight(request: Request, db: Session = Depends(get_db)) -> Response:
    """CORS preflight handler for /auth/login.

    Returns 204 with no body so nginx/frontends see a clean preflight response.
    Actual CORS headers are applied by the DynamicCORSMiddleware/nginx config.
    """
    origin = request.headers.get("origin")
    acrm = request.headers.get("access-control-request-method", "POST")
    acrh = request.headers.get("access-control-request-headers", "Authorization, Content-Type")

    # Build base headers
    headers = {
        "Access-Control-Allow-Methods": f"{acrm}, OPTIONS",
        "Access-Control-Allow-Headers": acrh,
        "Access-Control-Max-Age": "600",
    }
    # Only allow if origin is present and is approved
    if origin:
        allowed = _parse_env_allowed_origins()
        try:
            # 1) Global CORS origins
            rows = (
                db.query(TenantCORSOrigin)
                .filter(TenantCORSOrigin.is_global == True)  # noqa: E712
                .filter(TenantCORSOrigin.enabled == True)    # noqa: E712
                .all()
            )
            allowed.update([r.origin.strip() for r in rows if r.origin])

            # 2) Tenant-specific matching by hint: X-Tenant-Id or X-Tenant-Slug/X-Tenant
            tenant_id_hint = request.headers.get("x-tenant-id")
            tenant_slug_hint = request.headers.get("x-tenant-slug") or request.headers.get("x-tenant")

            tenant_from_host = None
            host = (request.headers.get("host") or "").split(":")[0]
            if host and "." in host:
                # naive subdomain as slug: <slug>.example.com
                sub = host.split(".")[0]
                tenant_from_host = sub if sub and sub not in {"localhost", "127", "127-0-0-1"} else None

            # Resolution order: prefer subdomain, then header hints
            tenant_obj = None
            subdomain_only = os.getenv("TENANTRA_CORS_SUBDOMAIN_ONLY", "0").lower() in {"1","true","yes","on"}
            if tenant_from_host:
                tenant_obj = db.query(Tenant).filter(Tenant.slug == tenant_from_host).first()
            if (tenant_obj is None) and not subdomain_only and tenant_id_hint:
                try:
                    tenant_obj = db.query(Tenant).filter(Tenant.id == int(tenant_id_hint)).first()
                except Exception:
                    tenant_obj = None
            if (tenant_obj is None) and not subdomain_only and tenant_slug_hint:
                tenant_obj = db.query(Tenant).filter(Tenant.slug == tenant_slug_hint).first()

            if tenant_obj is not None:
                match = (
                    db.query(TenantCORSOrigin)
                    .filter(TenantCORSOrigin.tenant_id == tenant_obj.id)
                    .filter(TenantCORSOrigin.origin == origin)
                    .filter(TenantCORSOrigin.enabled == True)  # noqa: E712
                    .first()
                )
                if match:
                    allowed.add(origin)

            # 3) Fallback: any tenant row that matches the origin and is enabled
            if origin not in allowed:
                any_match = (
                    db.query(TenantCORSOrigin)
                    .filter(TenantCORSOrigin.origin == origin)
                    .filter(TenantCORSOrigin.enabled == True)  # noqa: E712
                    .first()
                )
                if any_match:
                    allowed.add(origin)

        except Exception:
            # On DB error, rely solely on env list
            pass

        if origin in allowed:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Vary"] = "Origin"
            headers["Access-Control-Allow-Credentials"] = "true"

    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)

@router.get("/auth/me", response_model=UserOut)
def get_current_user_me(
    token: str = Depends(oauth2_scheme),  # pull Bearer token from Authorization header
    db: Session = Depends(get_db),        # DB session
):
    """
    Introspect the caller's access token and return their profile.
    Always includes 'role' so the frontend can gate admin-only UI.
    """
    payload = decode_access_token(token)  # decode and validate JWT
    if not payload:                       # reject if invalid/expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    sub = payload.get("sub")              # subject is the user id as a string
    try:
        user_id = int(sub)                # coerce to int; invalid → 401
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    user = db.query(User).filter(User.id == user_id).first()  # find user by id
    if not user:                                              # user id not found → 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Return the normalized user profile (now includes role)
    return UserOut(
        id=user.id,
        username=user.username,
        email=getattr(user, "email", None),
        is_active=bool(getattr(user, "is_active", True)),
        role=getattr(user, "role", None),
    )
