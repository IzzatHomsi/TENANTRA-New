from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping, Sequence
from urllib.parse import urlencode

from jinja2 import Template

from app.models.tenant import Tenant
from app.models.tenant_join_request import TenantJoinRequest
from app.models.user import User
from app.utils.email import send_email, send_email_alert


TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "email_templates"
PUBLIC_APP_URL = os.getenv("TENANTRA_PUBLIC_APP_URL", "http://localhost:5173")


def _load_template(filename: str) -> Template | None:
    path = TEMPLATE_DIR / filename
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            return Template(handle.read())
    except Exception:
        return None


def _build_frontend_url(path: str, query: Mapping[str, str] | None = None) -> str:
    base = PUBLIC_APP_URL.rstrip("/")
    if not path.startswith("/"):
        path = f"/{path}"
    url = f"{base}{path}"
    if query:
        url = f"{url}?{urlencode(query)}"
    return url


def _send_html_email(to: str, subject: str, template_name: str, context: Mapping[str, object], *, fallback: str) -> bool:
    template = _load_template(template_name)
    if template:
        try:
            html = template.render(**context)
            return send_email_alert(to=to, subject=subject, html_body=html, text_body=fallback, raise_on_error=False)
        except Exception:
            pass
    return send_email(to=to, subject=subject, body=fallback, raise_on_error=False)


def send_password_reset_email(user: User, token: str) -> bool:
    if not user.email:
        return False
    reset_url = _build_frontend_url("/reset-password", {"token": token})
    context = {"username": user.username, "reset_url": reset_url}
    fallback = f"Hello {user.username},\n\nUse the link below to reset your password:\n{reset_url}\n\nIf you did not request this action, please ignore this email."
    return _send_html_email(
        user.email,
        "Reset your Tenantra password",
        "password_reset_email.html",
        context,
        fallback=fallback,
    )


def send_verification_email(user: User, token: str) -> bool:
    if not user.email:
        return False
    verify_url = _build_frontend_url("/verify-email", {"token": token})
    context = {"username": user.username, "verify_url": verify_url}
    fallback = f"Welcome {user.username},\n\nVerify your Tenantra account by visiting:\n{verify_url}\n\nThe link will expire soon."
    return _send_html_email(
        user.email,
        "Verify your Tenantra account",
        "verify_email.html",
        context,
        fallback=fallback,
    )


def send_welcome_email(user: User) -> bool:
    if not user.email:
        return False
    fallback = (
        f"Hi {user.username},\n\n"
        "Your Tenantra workspace is ready. Sign in to start managing tenants, modules, and compliance automation."
    )
    return _send_html_email(
        user.email,
        "Welcome to Tenantra",
        "welcome_email.html",
        {"username": user.username},
        fallback=fallback,
    )


def notify_join_request_submitted(request_obj: TenantJoinRequest, tenant: Tenant, admin_emails: Sequence[str]) -> None:
    if not admin_emails:
        return
    fallback = (
        f"A new join request was submitted for tenant '{tenant.name}'.\n\n"
        f"Name: {request_obj.full_name}\nEmail: {request_obj.email}\nMessage: {request_obj.message or '-'}"
    )
    context = {
        "tenant_name": tenant.name,
        "full_name": request_obj.full_name,
        "email": request_obj.email,
        "message": request_obj.message or "",
    }
    for recipient in admin_emails:
        _send_html_email(
            recipient,
            f"Join request submitted for {tenant.name}",
            "join_request_notification.html",
            context,
            fallback=fallback,
        )


def acknowledge_join_request(request_obj: TenantJoinRequest, tenant: Tenant) -> None:
    if not request_obj.email:
        return
    fallback = (
        f"Hi {request_obj.full_name},\n\n"
        f"We received your request to join '{tenant.name}'. Tenant administrators have been notified and will review it shortly."
    )
    context = {
        "tenant_name": tenant.name,
        "full_name": request_obj.full_name,
        "message": request_obj.message or "",
    }
    _send_html_email(
        request_obj.email,
        f"We received your Tenantra join request for {tenant.name}",
        "join_request_acknowledgement.html",
        context,
        fallback=fallback,
    )


def notify_join_request_decision(request_obj: TenantJoinRequest) -> None:
    if not request_obj.email:
        return
    fallback = (
        f"Hi {request_obj.full_name},\n\n"
        f"Your request to join tenant '{request_obj.tenant.name}' was {request_obj.status}."
    )
    context = {
        "full_name": request_obj.full_name,
        "status": request_obj.status,
        "tenant_name": request_obj.tenant.name if request_obj.tenant else "",
        "decision_note": request_obj.decision_note or "",
    }
    _send_html_email(
        request_obj.email,
        f"Your Tenantra tenant request was {request_obj.status}",
        "join_request_decision.html",
        context,
        fallback=fallback,
    )
