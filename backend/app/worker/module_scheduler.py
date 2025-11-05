"""Background worker that executes scheduled module runs."""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.scheduled_scan import ScheduledScan
from app.services.module_executor import ModuleRunnerNotFound, execute_module
from app.services.schedule_utils import compute_next_run
from app.observability.metrics import record_scheduler_run

logger = logging.getLogger(__name__)


class ModuleSchedulerWorker(threading.Thread):
    def __init__(self, poll_interval: float = 30.0) -> None:
        super().__init__(daemon=True)
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()

    def run(self) -> None:  # pragma: no cover - background thread
        logger.info("Module scheduler worker started (interval=%ss)", self.poll_interval)
        while not self._stop_event.is_set():
            start = time.time()
            try:
                self._process_cycle()
            except Exception:  # pragma: no cover - defensive
                logger.exception("Module scheduler cycle failed")
            elapsed = time.time() - start
            remaining = max(self.poll_interval - elapsed, 1.0)
            self._stop_event.wait(remaining)
        logger.info("Module scheduler worker stopped")

    def stop(self, timeout: float | None = 5.0) -> None:
        self._stop_event.set()
        self.join(timeout=timeout)

    def _process_cycle(self) -> None:
        session = SessionLocal()
        try:
            now = datetime.utcnow()
            due_schedules = (
                session.query(ScheduledScan)
                .filter(ScheduledScan.enabled.is_(True))
                .filter(
                    (ScheduledScan.next_run_at == None)  # noqa: E711
                    | (ScheduledScan.next_run_at <= now)
                )
                .limit(25)
                .all()
            )

            for schedule in due_schedules:
                self._execute_schedule(session, schedule)

            session.commit()
        finally:
            session.close()

    def _execute_schedule(self, db: Session, schedule: ScheduledScan) -> None:
        module = schedule.module
        if module is None:
            schedule.status = "missing_module"
            schedule.enabled = False
            schedule.next_run_at = compute_next_run(schedule.cron_expr)
            return

        try:
            params = None
            try:
                params = getattr(schedule, "parameters", None)
            except Exception:
                params = None
            record = execute_module(
                db=db,
                module=module,
                tenant_id=schedule.tenant_id,
                agent_id=schedule.agent_id,
                user_id=None,
                parameters=params or {},
            )
            schedule.status = record.status
            schedule.last_run_at = record.recorded_at
            try:
                record_scheduler_run(schedule.status)
            except Exception:
                pass
        except ModuleRunnerNotFound:
            logger.warning("Schedule %s disabled: no runner for module %s", schedule.id, module.name)
            schedule.status = "no_runner"
            schedule.enabled = False
            try:
                record_scheduler_run(schedule.status)
            except Exception:
                pass
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Scheduled execution failed for module %s", module.name)
            schedule.status = "error"
            try:
                record_scheduler_run(schedule.status)
            except Exception:
                pass
        finally:
            schedule.next_run_at = compute_next_run(schedule.cron_expr, reference=datetime.utcnow())
            schedule.updated_at = datetime.utcnow()
