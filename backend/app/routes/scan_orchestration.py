"""Scan orchestration endpoints for scheduling and tracking jobs."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.agent import Agent
from app.models.asset import Asset
from app.models.scan_job import ScanJob, ScanResult
from app.models.user import User
from app.schemas.scan import (
    ScanJobCreate,
    ScanJobRead,
    ScanJobWithResults,
    ScanResultCreate,
    ScanResultRead,
)

router = APIRouter(prefix="/scan-orchestration", tags=["Scan Orchestration"])


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id required")
    return tenant_id


@router.get("/jobs", response_model=List[ScanJobRead])
def list_jobs(
    status: Optional[str] = Query(None),
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ScanJobRead]:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    query = db.query(ScanJob).filter(ScanJob.tenant_id == resolved_tenant)
    if status:
        query = query.filter(ScanJob.status == status)
    jobs = query.order_by(ScanJob.created_at.desc()).all()
    return [ScanJobRead.from_orm(job) for job in jobs]


@router.post("/jobs", response_model=ScanJobRead, status_code=201)
def create_job(
    payload: ScanJobCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScanJobRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    job = ScanJob(
        tenant_id=resolved_tenant,
        name=payload.name,
        description=payload.description,
        scan_type=payload.scan_type,
        priority=payload.priority,
        schedule=payload.schedule,
        status="pending",
        created_by=current_user.id,
        created_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return ScanJobRead.from_orm(job)


@router.get("/jobs/{job_id}", response_model=ScanJobWithResults)
def get_job(
    job_id: int = Path(...),
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScanJobWithResults:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    job = (
        db.query(ScanJob)
        .filter(ScanJob.id == job_id, ScanJob.tenant_id == resolved_tenant)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return ScanJobWithResults(
        job=ScanJobRead.from_orm(job),
        results=[ScanResultRead.from_orm(result) for result in job.results],
    )


@router.post("/jobs/{job_id}/results", response_model=ScanResultRead, status_code=201)
def add_result(
    job_id: int = Path(...),
    payload: ScanResultCreate = Body(...),
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScanResultRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    job = (
        db.query(ScanJob)
        .filter(ScanJob.id == job_id, ScanJob.tenant_id == resolved_tenant)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if payload.agent_id:
        agent = db.query(Agent).filter(Agent.id == payload.agent_id).first()
        if not agent or (agent.tenant_id and agent.tenant_id != resolved_tenant):
            raise HTTPException(status_code=400, detail="Agent scope invalid")
    if payload.asset_id:
        asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
        if not asset or asset.tenant_id != resolved_tenant:
            raise HTTPException(status_code=400, detail="Asset scope invalid")
    result = ScanResult(
        job_id=job.id,
        agent_id=payload.agent_id,
        asset_id=payload.asset_id,
        status=payload.status,
        details=payload.details,
        started_at=datetime.utcnow() if payload.status in {"running", "completed"} else None,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return ScanResultRead.from_orm(result)


@router.post("/results/{result_id}/status", response_model=ScanResultRead)
def update_result_status(
    result_id: int = Path(...),
    status: str = Query(..., description="New status for the result"),
    details: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScanResultRead:
    result = db.query(ScanResult).filter(ScanResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    parent = db.query(ScanJob).filter(ScanJob.id == result.job_id).first()
    if current_user.tenant_id is not None and parent.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    result.status = status
    if status == "completed":
        result.completed_at = datetime.utcnow()
    if details:
        result.details = details
    db.add(result)
    if status in {"running"} and result.started_at is None:
        result.started_at = datetime.utcnow()
    db.commit()
    db.refresh(result)
    return ScanResultRead.from_orm(result)
