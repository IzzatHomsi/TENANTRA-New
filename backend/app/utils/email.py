import os
import smtplib
from email.message import EmailMessage
from typing import Optional

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "no-reply@tenantra.local")
SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() in ("1","true","yes")
SMTP_TIMEOUT = float(os.getenv("SMTP_TIMEOUT", "5"))

class EmailError(Exception):
    pass

def _deliver_message(msg: EmailMessage, *, raise_on_error: bool = False) -> bool:
    """Send an ``EmailMessage`` using the configured SMTP settings."""
    try:
        if not SMTP_HOST:
            # Misconfigured: pretend failure
            if raise_on_error:
                raise EmailError("SMTP_HOST not configured")
            return False

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            if SMTP_TLS:
                server.starttls()
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as ex:
        if raise_on_error:
            raise EmailError(str(ex))
        return False


def send_email(to: str, subject: str, body: str, *, raise_on_error: bool = False) -> bool:
    """
    Send a simple email. Returns True on success, False on failure unless ``raise_on_error`` is
    ``True``. Designed to be safe in production pipelines: default is non-throwing.
    """
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    return _deliver_message(msg, raise_on_error=raise_on_error)


def send_email_alert(
    to: str,
    subject: str,
    html_body: str,
    *,
    text_body: Optional[str] = None,
    raise_on_error: bool = False,
) -> bool:
    """Send an HTML alert e-mail.

    ``text_body`` may be supplied to override the default plain-text fallback used for clients that
    cannot render HTML.
    """

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text_body or "This alert requires an HTML-capable e-mail client.")
    msg.add_alternative(html_body, subtype="html")

    return _deliver_message(msg, raise_on_error=raise_on_error)
