"""Celery task for scheduled scan processing."""

from __future__ import annotations

import logging

from app.celery_app import celery_app
from app.services.scheduler_service import process_due_schedules

logger = logging.getLogger("tenantra.tasks.scheduler")


@celery_app.task(name="tenantra.scheduler.tick")
def run_scheduler_cycle() -> dict[str, int]:
    processed = process_due_schedules()
    logger.debug("Scheduler processed %s schedules", processed)
    return {"processed": processed}
