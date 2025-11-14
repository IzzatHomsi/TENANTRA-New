"""Scheduled scan processing helpers."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.scan_job import ScanJob
from app.observability.metrics import record_scheduler_run
from app.services.module_executor import ModuleRunnerNotFound, execute_module
from app.services.schedule_utils import compute_next_run

logger = logging.getLogger("tenantra.scheduler")


def _fetch_due_jobs(session: Session, limit: int) -> List[ScanJob]:
    now = datetime.utcnow()
    query = (
        session.query(ScanJob)
        .filter(ScanJob.scan_type == "module")
        .filter(ScanJob.enabled.is_(True))
        .filter(
            or_(
                ScanJob.next_run_at == None,  # noqa: E711
                ScanJob.next_run_at <= now,
            )
        )
        .order_by(ScanJob.next_run_at.asc())
        .limit(limit)
    )
    try:
        query = query.with_for_update(skip_locked=True)
    except Exception:
        # SQLite and some test transports do not support SKIP LOCKED.
        pass
    return query.all()


def _execute_job(session: Session, job: ScanJob) -> None:
    module = job.module
    if module is None:
        job.status = "missing_module"
        job.enabled = False
        job.next_run_at = compute_next_run(job.schedule)
        return

    try:
        params = getattr(job, "parameters", None) or {}
        record = execute_module(
            db=session,
            module=module,
            tenant_id=job.tenant_id,
            agent_id=job.agent_id,
            user_id=None,
            parameters=params,
        )
        job.status = record.status
        job.last_run_at = record.recorded_at
        job.started_at = record.recorded_at
        job.completed_at = record.recorded_at
        record_scheduler_run(job.status)
    except ModuleRunnerNotFound:
        logger.warning("Job %s disabled: no runner for module %s", job.id, module.name)
        job.status = "no_runner"
        job.enabled = False
        try:
            record_scheduler_run(job.status)
        except Exception:
            pass
    except Exception:
        logger.exception("Scheduled execution failed for module %s", getattr(module, "name", "unknown"))
        job.status = "error"
        try:
            record_scheduler_run(job.status)
        except Exception:
            pass
    finally:
        job.next_run_at = compute_next_run(job.schedule, reference=datetime.utcnow())
        job.updated_at = datetime.utcnow()


def process_due_schedules(batch_size: int = 25) -> int:
    """Process due schedules in a single transaction."""
    processed = 0
    with get_db_session() as session:
        jobs = _fetch_due_jobs(session, batch_size)
        if not jobs:
            return 0
        for job in jobs:
            _execute_job(session, job)
            processed += 1
        session.commit()
    return processed
