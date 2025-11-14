"""Scheduling endpoints for module scans."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.module import Module
from app.models.scan_job import ScanJob
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleOut
from app.services.schedule_utils import compute_next_run

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.get("", response_model=List[ScheduleOut])
def list_schedules(
    module_id: Optional[int] = Query(None, description="Filter schedules by module"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ScheduleOut]:
    query = db.query(ScanJob).filter(ScanJob.scan_type == "module")

    if current_user.tenant_id:
        query = query.filter(ScanJob.tenant_id == current_user.tenant_id)

    if module_id is not None:
        query = query.filter(ScanJob.module_id == module_id)

    rows = query.order_by(ScanJob.id.desc()).limit(200).all()
    return [ScheduleOut.from_orm(row) for row in rows]


@router.post(
    "",
    response_model=ScheduleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScheduleOut:
    _ensure_admin(current_user)
    tenant_id = payload.tenant_id or current_user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id is required for scheduling")

    module = db.query(Module).filter(Module.id == payload.module_id).first()
    if module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    schedule = ScanJob(
        tenant_id=tenant_id,
        name=f"{module.name} schedule",
        description="Module execution schedule",
        scan_type="module",
        priority="normal",
        schedule=payload.cron_expr,
        status="scheduled",
        created_by=current_user.id,
        module_id=module.id,
        agent_id=payload.agent_id,
        parameters=payload.parameters or None,
        enabled=True,
        next_run_at=compute_next_run(payload.cron_expr),
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return ScheduleOut.from_orm(schedule)


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    _ensure_admin(current_user)
    schedule = db.query(ScanJob).filter(ScanJob.id == schedule_id, ScanJob.scan_type == "module").first()
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    if current_user.tenant_id and schedule.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Schedule belongs to a different tenant")

    db.delete(schedule)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _ensure_admin(user: User) -> None:
    role_value = getattr(user, "role", None)
    if role_value is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    if isinstance(role_value, (list, tuple, set)):
        roles = {str(r).strip().lower() for r in role_value}
    else:
        roles = {str(role_value).strip().lower()}
    if not roles & {"admin", "super_admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
