# backend/app/worker/run_notifications_worker.py
"""
Long-running notifications worker entrypoint for Docker.

Problem (before):
- The process started a worker and then called `time.sleep(1)`, returning 0 after one second.
- PID 1 exited cleanly, so Docker restarted the container repeatedly.

Solution (now):
- Install SIGINT/SIGTERM handlers and block the main thread on an Event until a stop signal arrives.
- Optionally honor TENANTRA_ENABLE_NOTIFICATIONS_WORKER=0 to idle without crashes.

This module is executed via: `python -m app.worker.run_notifications_worker`
"""

from __future__ import annotations  # future-proof type hints (no runtime effect)
import logging                      # structured logs to stdout for Docker
import os                           # read feature flags from environment
import signal                       # catch container stop signals
import sys                          # set exit code on shutdown
import threading                    # Event() to block until signalled
from app.worker.notifications_worker import NotificationsWorker  # actual worker implementation
from app.worker.health_api import build_app
import threading as _threading
import uvicorn

# ---------- logging setup ----------
logging.basicConfig(                  # configure root logger once for container
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("tenantra.worker")  # dedicated logger for clarity


def main() -> int:
    """
    Start the notifications worker (if enabled) and block until SIGINT/SIGTERM.

    Returns:
        int: process exit code (0 on clean shutdown).
    """
    # Feature flag: allow disabling the worker without changing compose.
    # Any of "0", "false", "False" disables; everything else enables.
    enabled_raw = os.getenv("TENANTRA_ENABLE_NOTIFICATIONS_WORKER", "1")
    enabled = enabled_raw not in {"0", "false", "False"}

    stop_event = threading.Event()   # used to block the main thread until a signal arrives
    worker: NotificationsWorker | None = None  # reference for clean shutdown

    # --- signal handlers: flip the event so main thread can exit gracefully ---
    def _handle_stop(signum, _frame):
        log.info("Received signal %s — stopping worker...", signum)
        stop_event.set()

    # Register for typical Docker stop signals
    signal.signal(signal.SIGINT, _handle_stop)   # CTRL+C / container stop
    signal.signal(signal.SIGTERM, _handle_stop)  # docker stop / orchestrator

    try:
        # Start lightweight health HTTP server in background
        def _serve_health():
            app = build_app()
            # Bind to localhost by default; allow override via env to opt-in to 0.0.0.0 in containers
            host = os.getenv("WORKER_HEALTH_HOST", "127.0.0.1")
            uvicorn.run(app, host=host, port=int(os.getenv("WORKER_HEALTH_PORT", "8081")), log_level="warning")

        _health_thread = _threading.Thread(target=_serve_health, name="worker-health", daemon=True)
        _health_thread.start()

        if enabled:
            # Instantiate and start the worker (implementation-managed threads/processes).
            worker = NotificationsWorker()
            worker.start()
            log.info("Notifications worker started.")
        else:
            # If disabled, do not start any background activity; just idle until stopped.
            log.info("Notifications worker DISABLED by TENANTRA_ENABLE_NOTIFICATIONS_WORKER=%s — idling.", enabled_raw)

        # --- BLOCK HERE until a stop signal is received ---
        # .wait(None) -> indefinite block; returns True when set, else never returns.
        stop_event.wait()
        log.info("Shutdown requested. Commencing graceful stop...")

    except Exception as exc:
        # If the worker raised unexpectedly, log and request shutdown.
        log.exception("Worker encountered an unhandled exception: %s", exc)
        stop_event.set()
        # We still attempt clean stop below, then return non-zero.
        exit_code = 1
    else:
        exit_code = 0
    finally:
        # Attempt a clean stop if the worker was started.
        if worker is not None:
            try:
                worker.stop(timeout=5.0)  # ask the worker to finish quickly
                log.info("Worker stopped cleanly.")
            except Exception as exc:
                log.exception("Error while stopping worker: %s", exc)
                exit_code = 1

    return exit_code


if __name__ == "__main__":
    # Run main() and use its return value as process exit code for Docker.
    sys.exit(main())
