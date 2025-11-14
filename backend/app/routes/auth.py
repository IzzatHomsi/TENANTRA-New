# backend/app/routes/auth.py
# Authentication routes: robust /auth/login (form or JSON) and /auth/me

from typing import Optional, Tuple  # import Optional for fields that may be None
from datetime import datetime
import os
import secrets
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response  # FastAPI primitives
from fastapi.security import OAuth2PasswordBearer  # OAuth2 token extractor from Authorization header
from sqlalchemy.orm import Session  # SQLAlchemy session type for DB work
from sqlalchemy import func
from pydantic import BaseModel, EmailStr, root_validator  # Pydantic models for request/response typing

from app.database import get_db  # dependency that yields a DB session
from app.models.tenant_cors_origin import TenantCORSOrigin
from app.models.tenant import Tenant
from app.models.user import User  # ORM model for users table
from app.core.security import verify_password, create_access_token, decode_access_token  # crypto helpers
from app.core.auth import get_current_user
from app.core.security import get_password_hash
from app.services import password_reset as password_reset_service, token_blocklist
from app.utils.email import send_email
from app.utils.password import validate_password_strength, PasswordValidationError
from app.utils.audit import log_audit_event

# Create a router; app mounts this under /api in main.py
router = APIRouter()
logger = logging.getLogger("tenantra.auth")

# Extract Bearer tokens sent to protected endpoints (e.g., /auth/me)
# tokenUrl informs OpenAPI docs where tokens are obtained.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
_TRUE_VALUES = {"1", "true", "yes", "on"}
_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def _slugify_tenant(value: str) -> str:
    cleaned = _SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return cleaned or f"tenant-{secrets.token_hex(3)}"


def _unique_tenant_labels(db: Session, desired_name: str) -> Tuple[str, str]:
    """
    Return a unique (tenant_name, slug) tuple derived from ``desired_name``.
    """
    base_name = (desired_name or "").strip() or "New Tenant"
    name_candidate = base_name
    suffix = 1
    while db.query(Tenant).filter(Tenant.name == name_candidate).first():
        suffix += 1
        name_candidate = f"{base_name} {suffix}"

    slug_candidate = _slugify_tenant(name_candidate)
    slug_value = slug_candidate
    slug_suffix = 1
    while db.query(Tenant).filter(Tenant.slug == slug_value).first():
        slug_suffix += 1
        slug_value = f"{slug_candidate}-{slug_suffix}"

    return name_candidate, slug_value


def _is_test_mode() -> bool:
    return bool(
        os.getenv("PYTEST_CURRENT_TEST")
        or os.getenv("TENANTRA_TEST_BOOTSTRAP", "").lower() in _TRUE_VALUES
    )


def _exp_to_datetime(value: Optional[int]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.utcfromtimestamp(int(value))
    except Exception:
        return None

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

class ForgotPasswordPayload(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

    @root_validator(skip_on_failure=True)
    def ensure_target(cls, values):
        if not values.get("username") and not values.get("email"):
            raise ValueError("Provide a username or email address.")
        return values


class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str


class RegistrationRequest(BaseModel):
    tenant_name: str
    username: str
    email: EmailStr
    password: str


class RegistrationResponse(BaseModel):
    tenant_id: int
    tenant_slug: str
    user_id: int
    requires_verification: bool = False

# ---------- Routes ----------


@router.post("/auth/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegistrationRequest,
    db: Session = Depends(get_db),
) -> RegistrationResponse:
    username = (payload.username or "").strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")
    tenant_name_input = (payload.tenant_name or "").strip()
    email = (payload.email or "").strip().lower()

    if db.query(User).filter(func.lower(User.username) == username.lower()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    if db.query(User).filter(func.lower(User.email) == email.lower()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    try:
        validate_password_strength(payload.password)
    except PasswordValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    tenant_name, tenant_slug = _unique_tenant_labels(db, tenant_name_input or username)

    try:
        tenant = Tenant(name=tenant_name, slug=tenant_slug, is_active=True)
        db.add(tenant)
        db.flush()

        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(payload.password),
            role="admin",
            tenant_id=tenant.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Registration failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed") from exc

    log_audit_event(
        db,
        user_id=user.id,
        action="auth.register",
        result="success",
        details={"tenant_id": tenant.id},
    )

    message = (
        f"Hi {username},\n\n"
        f"Your tenant '{tenant_name}' is ready. You can sign in at /login with the credentials you just created."
    )
    try:
        send_email(email, "Welcome to Tenantra", message)
    except Exception:
        logger.warning("Failed to send registration confirmation e-mail to %s", email)

    return RegistrationResponse(
        tenant_id=tenant.id,
        tenant_slug=tenant.slug,
        user_id=user.id,
        requires_verification=False,
    )


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


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    token_blocklist.revoke_token(
        db,
        user_id=current_user.id,
        jti=payload.get("jti"),
        expires_at=_exp_to_datetime(payload.get("exp")),
        reason="logout",
    )
    log_audit_event(
        db,
        user_id=current_user.id,
        action="auth.logout",
        result="success",
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.post("/auth/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(
    payload: ForgotPasswordPayload,
    request: Request,
    db: Session = Depends(get_db),
):
    user: Optional[User] = None
    if payload.username:
        user = db.query(User).filter(User.username == payload.username).first()
    elif payload.email:
        user = db.query(User).filter(User.email == payload.email).first()

    response = {"status": "queued"}
    if user:
        raw_token = password_reset_service.issue_password_reset_token(
            db,
            user,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
        )
        log_audit_event(
            db,
            user_id=user.id,
            action="auth.forgot_password",
            result="success",
            ip=request.client.host if request.client else None,
        )
        if user.email:
            send_email(
                user.email,
                "Tenantra password reset",
                f"Use this token to reset your password: {raw_token}",
            )
        if _is_test_mode():
            response["reset_token"] = raw_token
    return response

@router.get("/auth/me", response_model=UserOut)
def get_current_user_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=getattr(current_user, "email", None),
        is_active=bool(getattr(current_user, "is_active", True)),
        role=getattr(current_user, "role", None),
    )


@router.post("/auth/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    payload: ResetPasswordPayload,
    db: Session = Depends(get_db),
):
    try:
        validate_password_strength(payload.new_password)
    except PasswordValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    try:
        token_record = password_reset_service.use_password_reset_token(db, payload.token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.password_hash = get_password_hash(payload.new_password)
    db.add(user)
    db.commit()
    token_blocklist.revoke_tokens_issued_before(
        db,
        user_id=user.id,
        cutoff=datetime.utcnow(),
        reason="password_reset",
    )
    log_audit_event(
        db,
        user_id=user.id,
        action="auth.reset_password",
        result="success",
    )
    return {"status": "ok"}
