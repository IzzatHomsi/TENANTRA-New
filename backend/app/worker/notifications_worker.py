# backend/app/worker/notifications_worker.py
# ----------------------------------------------------------------------
# Signal-free notifications worker:
# - No use of OS signals (which break in non-main threads / uvicorn workers).
# - Controlled by threading.Event + daemon Thread.
# - Start/stop from FastAPI startup/shutdown (wired in app/main.py).
# - Put your real dispatch logic inside process_once().
# ----------------------------------------------------------------------

import threading
import time
import logging
from datetime import datetime
from typing import Optional, List

from app.db.session import get_db_session
from app.models.notification import Notification
from app.models.notification_log import NotificationLog
from app.utils.email import send_email

logger = logging.getLogger("tenantra.notifications.worker")


class NotificationsWorker:
    """
    Background worker for notifications dispatch.

    Start with .start(), stop with .stop(). The loop runs every poll_interval_seconds
    and calls process_once() safely (exceptions are contained and logged).
    """

    def __init__(self, poll_interval_seconds: int = 10) -> None:
        # poll interval between iterations (seconds)
        self.poll_interval_seconds = poll_interval_seconds
        # event used to request a graceful shutdown
        self._stop_event = threading.Event()
        # thread handle for the daemon worker
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the worker thread if not already running."""
        if self._thread and self._thread.is_alive():
            logger.info("Notifications worker already running.")
            return

        self._thread = threading.Thread(
            target=self._run_loop,
            name="notifications-worker",
            daemon=True,   # daemon ensures the thread won't block process exit
        )
        self._thread.start()
        logger.info("Notifications worker started.")

    def stop(self, timeout: float = 5.0) -> None:
        """Signal the worker to stop and wait up to `timeout` seconds."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning("Notifications worker did not stop within timeout.")
            else:
                logger.info("Notifications worker stopped cleanly.")
        # reset for a potential future restart in same process (tests, hot-reload)
        self._thread = None
        self._stop_event.clear()

    def _run_loop(self) -> None:
        """Internal main loop; never raises outwards."""
        logger.debug("Notifications worker loop started.")
        try:
            while not self._stop_event.is_set():
                try:
                    self.process_once()  # execute one unit of work
                except Exception as exc:
                    # Never let one failure kill the loop
                    logger.exception("Notifications worker iteration failed: %s", exc)
                # Sleep until next tick or stop signal
                self._stop_event.wait(timeout=self.poll_interval_seconds)
        finally:
            logger.debug("Notifications worker loop exiting.")

    # ------------------------------------------------------------------
    # Put your real notification logic here (DB fetch -> send -> mark).
    # Keep it fast and robust; do retries/backoff outside critical path.
    # ------------------------------------------------------------------
    def process_once(self) -> None:
        logger.debug("Notifications worker heartbeat (process_once).")
        with get_db_session() as db:
            pending: List[Notification] = (
                db.query(Notification)
                .filter(Notification.status == "queued")
                .order_by(Notification.id.asc())
                .limit(20)
                .all()
            )
            if not pending:
                return
            for note in pending:
                try:
                    ok = send_email(note.recipient_email, note.title, note.message, raise_on_error=False)
                    if ok:
                        note.status = "sent"
                        note.sent_at = datetime.utcnow()
                        db.add(
                            NotificationLog(
                                tenant_id=note.tenant_id,
                                notification_id=note.id,
                                channel="email",
                                recipient=note.recipient_email,
                                subject=note.title,
                                body=None,
                                status="sent",
                                error=None,
                            )
                        )
                    else:
                        note.status = "failed"
                        db.add(
                            NotificationLog(
                                tenant_id=note.tenant_id,
                                notification_id=note.id,
                                channel="email",
                                recipient=note.recipient_email,
                                subject=note.title,
                                body=None,
                                status="failed",
                                error="delivery_failed",
                            )
                        )
                    db.commit()
                except Exception:
                    logger.exception("Failed to dispatch notification id=%s", getattr(note, "id", None))
                    try:
                        db.rollback()
                    except Exception:
                        pass
        return
