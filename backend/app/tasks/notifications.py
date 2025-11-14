"""Celery task for notification dispatch."""

from __future__ import annotations

import logging

from app.celery_app import celery_app
from app.services.notification_dispatcher import dispatch_pending_notifications

logger = logging.getLogger("tenantra.tasks.notifications")


@celery_app.task(name="tenantra.notifications.dispatch")
def dispatch_notifications_task() -> dict[str, int]:
    processed = dispatch_pending_notifications()
    logger.debug("Notification dispatcher processed %s messages", processed)
    return {"processed": processed}
