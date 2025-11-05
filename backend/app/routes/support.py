"""Support & outreach endpoints (staging CTA).

POST /support/walkthrough accepts a request to schedule a walkthrough.
Stores an audit entry and returns 202 Accepted. In production, this can
enqueue an email/notification; here we keep it minimal and side-effect-safe.
"""

from datetime import datetime
import os
from typing import Optional

from fastapi import APIRouter, Request, status, Depends
from pydantic import BaseModel, Field, constr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.audit import log_audit_event
from app.utils.email import send_email, send_email_alert
from jinja2 import Template
from sqlalchemy import func
from app.models.notification import Notification


router = APIRouter(prefix="/support", tags=["Support"])

# Include admin settings routes under the same module to ensure mounting
try:
    from .app_settings import router as settings_router
    router.include_router(settings_router)
except Exception:
    pass

# Admin modules management
try:
    from .modules_admin import router as modules_admin_router
    router.include_router(modules_admin_router)
except Exception:
    pass

# Admin application logs
try:
    from .app_logs import router as app_logs_router
    router.include_router(app_logs_router)
except Exception:
    pass

# Admin observability helpers
try:
    from .observability_admin import router as obs_router
    router.include_router(obs_router)
except Exception:
    pass


class WalkthroughRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: constr(strip_whitespace=True, min_length=5, max_length=200)  # basic validation
    company: Optional[str] = Field(None, max_length=200)
    plan: Optional[str] = Field(None, max_length=100)
    referrer: Optional[str] = Field(None, max_length=300)


@router.post("/walkthrough", status_code=status.HTTP_202_ACCEPTED)
def request_walkthrough(
    payload: WalkthroughRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    current_user: Optional[User] = None  # unauthenticated allowed
    try:
        ip = request.client.host if request.client else None
        # Log an audit entry (do not fail main flow on errors)
        log_audit_event(
            db,
            user_id=getattr(current_user, "id", None),
            action="request_walkthrough",
            result="submitted",
            ip=ip,
            timestamp=datetime.utcnow(),
        )
    except Exception:
        # Intentionally swallow audit errors
        pass

    # Send a real e-mail via configured SMTP provider. Non-throwing by default.
    subject = "Tenantra Walkthrough Request"
    submitted_at = datetime.utcnow().isoformat() + "Z"
    # Render HTML template
    template_path = os.path.join(os.path.dirname(__file__), "../email_templates/walkthrough_email.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = Template(f.read())
        html = html_template.render(
            name=payload.name,
            email=payload.email,
            company=payload.company,
            plan=payload.plan,
            referrer=payload.referrer,
            submitted_at=submitted_at,
        )
    except Exception:
        html = None

    # Plain text fallback
    text_lines = [
        f"Name: {payload.name}",
        f"Email: {payload.email}",
        f"Company: {payload.company or '-'}",
        f"Plan: {payload.plan or '-'}",
        f"Referrer: {payload.referrer or '-'}",
        f"SubmittedAt: {submitted_at}",
    ]

    recipient = os.getenv("TENANTRA_WALKTHROUGH_RECIPIENT", "Tenantra.info@homsi-co.com")
    queued = False
    # If a tenant context exists (e.g., authenticated caller), enqueue a notification instead of direct-send
    try:
        # Try to infer tenant by matching email to a known user, if any (best-effort)
        user = db.query(User).filter(func.lower(User.email) == payload.email.lower()).first()
        tenant_id = getattr(user, "tenant_id", None)
        if tenant_id is not None:
            note = Notification(
                tenant_id=tenant_id,
                recipient_id=None,
                recipient_email=recipient,
                title=subject,
                message=f"Walkthrough requested by {payload.name} <{payload.email}>",
                severity="info",
                status="queued",
            )
            db.add(note)
            db.commit()
            queued = True
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass

    if queued:
        email_ok = True  # will be delivered by worker
    else:
        if html:
            email_ok = send_email_alert(to=recipient, subject=subject, html_body=html, text_body="\n".join(text_lines), raise_on_error=False)
        else:
            email_ok = send_email(to=recipient, subject=subject, body="\n".join(text_lines), raise_on_error=False)

    # Return minimal echo (redacted) for client confirmation
    return {
        "message": "Walkthrough request accepted",
        "email_sent": bool(email_ok),
        "queued": queued,
        "submitted": {
            "name": payload.name,
            "email_hash_len": len(payload.email),
            "company": payload.company,
            "plan": payload.plan,
            "referrer": payload.referrer,
        },
    }

