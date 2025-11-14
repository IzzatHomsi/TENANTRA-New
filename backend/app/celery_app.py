"""Celery application instance for Tenantra background tasks."""

from __future__ import annotations

import os

from celery import Celery
from celery.schedules import schedule


def _create_celery() -> Celery:
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    backend_url = os.getenv("CELERY_RESULT_BACKEND", broker_url)
    app = Celery(
        "tenantra",
        broker=broker_url,
        backend=backend_url,
        include=[
            "app.tasks.notifications",
            "app.tasks.scheduler",
        ],
    )
    default_queue = os.getenv("CELERY_DEFAULT_QUEUE", "tenantra")
    app.conf.task_default_queue = default_queue
    app.conf.result_expires = int(os.getenv("CELERY_RESULT_EXPIRES", "600"))

    notif_interval = float(os.getenv("TENANTRA_NOTIFICATIONS_INTERVAL", "10"))
    sched_interval = float(os.getenv("TENANTRA_SCHEDULER_INTERVAL", "30"))
    app.conf.beat_schedule = {
        "dispatch-notifications": {
            "task": "tenantra.notifications.dispatch",
            "schedule": schedule(notif_interval),
        },
        "process-scheduled-scans": {
            "task": "tenantra.scheduler.tick",
            "schedule": schedule(sched_interval),
        },
    }
    return app


celery_app = _create_celery()
