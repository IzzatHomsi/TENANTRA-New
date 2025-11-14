"""Notification delivery helpers used by Celery tasks."""

from __future__ import annotations

import logging
from datetime import datetime

from app.db.session import get_db_session
from app.models.notification import Notification
from app.models.notification_log import NotificationLog
from app.utils.email import send_email

logger = logging.getLogger("tenantra.notifications.dispatcher")


def dispatch_pending_notifications(batch_size: int = 20) -> int:
    """Send queued notifications and record delivery logs."""
    sent = 0
    with get_db_session() as db:
        pending = (
            db.query(Notification)
            .filter(Notification.status == "queued")
            .order_by(Notification.id.asc())
            .limit(batch_size)
            .all()
        )
        if not pending:
            return 0
        for note in pending:
            try:
                ok = send_email(note.recipient_email, note.title, note.message, raise_on_error=False)
                sent_at = datetime.utcnow()
                if ok:
                    note.status = "sent"
                    note.sent_at = sent_at
                    status = "sent"
                    error = None
                    sent += 1
                else:
                    note.status = "failed"
                    status = "failed"
                    error = "delivery_failed"
                db.add(
                    NotificationLog(
                        tenant_id=note.tenant_id,
                        notification_id=note.id,
                        channel="email",
                        recipient=note.recipient_email,
                        subject=note.title,
                        body=None,
                        status=status,
                        error=error,
                    )
                )
                db.commit()
            except Exception:
                logger.exception("Failed to dispatch notification id=%s", getattr(note, "id", None))
                try:
                    db.rollback()
                except Exception:
                    pass
    return sent
