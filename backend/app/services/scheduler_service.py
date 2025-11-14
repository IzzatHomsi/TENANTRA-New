"""Scheduled scan processing helpers."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.scheduled_scan import ScheduledScan
from app.observability.metrics import record_scheduler_run
from app.services.module_executor import ModuleRunnerNotFound, execute_module
from app.services.schedule_utils import compute_next_run

logger = logging.getLogger("tenantra.scheduler")


def _fetch_due_schedules(session: Session, limit: int) -> List[ScheduledScan]:
    now = datetime.utcnow()
    query = (
        session.query(ScheduledScan)
        .filter(ScheduledScan.enabled.is_(True))
        .filter(
            or_(
                ScheduledScan.next_run_at == None,  # noqa: E711
                ScheduledScan.next_run_at <= now,
            )
        )
        .order_by(ScheduledScan.next_run_at.asc())
        .limit(limit)
    )
    try:
        query = query.with_for_update(skip_locked=True)
    except Exception:
        # SQLite and some test transports do not support SKIP LOCKED.
        pass
    return query.all()


def _execute_schedule(session: Session, schedule: ScheduledScan) -> None:
    module = schedule.module
    if module is None:
        schedule.status = "missing_module"
        schedule.enabled = False
        schedule.next_run_at = compute_next_run(schedule.cron_expr)
        return

    try:
        params = getattr(schedule, "parameters", None) or {}
        record = execute_module(
            db=session,
            module=module,
            tenant_id=schedule.tenant_id,
            agent_id=schedule.agent_id,
            user_id=None,
            parameters=params,
        )
        schedule.status = record.status
        schedule.last_run_at = record.recorded_at
        record_scheduler_run(schedule.status)
    except ModuleRunnerNotFound:
        logger.warning("Schedule %s disabled: no runner for module %s", schedule.id, module.name)
        schedule.status = "no_runner"
        schedule.enabled = False
        try:
            record_scheduler_run(schedule.status)
        except Exception:
            pass
    except Exception:
        logger.exception("Scheduled execution failed for module %s", getattr(module, "name", "unknown"))
        schedule.status = "error"
        try:
            record_scheduler_run(schedule.status)
        except Exception:
            pass
    finally:
        schedule.next_run_at = compute_next_run(schedule.cron_expr, reference=datetime.utcnow())
        schedule.updated_at = datetime.utcnow()


def process_due_schedules(batch_size: int = 25) -> int:
    """Process due schedules in a single transaction."""
    processed = 0
    with get_db_session() as session:
        schedules = _fetch_due_schedules(session, batch_size)
        if not schedules:
            return 0
        for schedule in schedules:
            _execute_schedule(session, schedule)
            processed += 1
        session.commit()
    return processed
