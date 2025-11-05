"""Tenant retention configuration and export endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.retention_policy import DataExportJob, TenantRetentionPolicy
from app.models.user import User
from app.schemas.retention import (
    DataExportJobCreate,
    DataExportJobRead,
    TenantRetentionPolicyRead,
    TenantRetentionPolicyUpdate,
)

router = APIRouter(prefix="/retention", tags=["Retention"])


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id required")
    return tenant_id


@router.get("/policy", response_model=TenantRetentionPolicyRead)
def get_policy(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TenantRetentionPolicyRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    policy = (
        db.query(TenantRetentionPolicy)
        .filter(TenantRetentionPolicy.tenant_id == resolved_tenant)
        .first()
    )
    if not policy:
        policy = TenantRetentionPolicy(tenant_id=resolved_tenant)
        db.add(policy)
        db.commit()
        db.refresh(policy)
    return TenantRetentionPolicyRead.from_orm(policy)


@router.put("/policy", response_model=TenantRetentionPolicyRead)
def update_policy(
    payload: TenantRetentionPolicyUpdate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TenantRetentionPolicyRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    policy = (
        db.query(TenantRetentionPolicy)
        .filter(TenantRetentionPolicy.tenant_id == resolved_tenant)
        .first()
    )
    if not policy:
        policy = TenantRetentionPolicy(tenant_id=resolved_tenant)
        db.add(policy)
        db.flush()
    policy.retention_days = payload.retention_days
    policy.archive_storage = payload.archive_storage
    policy.export_formats = ",".join(payload.export_formats)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return TenantRetentionPolicyRead.from_orm(policy)


@router.get("/exports", response_model=List[DataExportJobRead])
def list_exports(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DataExportJobRead]:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    exports = (
        db.query(DataExportJob)
        .filter(DataExportJob.tenant_id == resolved_tenant)
        .order_by(DataExportJob.requested_at.desc())
        .all()
    )
    return [DataExportJobRead.from_orm(job) for job in exports]


@router.post("/exports", response_model=DataExportJobRead, status_code=201)
def request_export(
    payload: DataExportJobCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DataExportJobRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    policy = (
        db.query(TenantRetentionPolicy)
        .filter(TenantRetentionPolicy.tenant_id == resolved_tenant)
        .first()
    )
    allowed_formats = set(policy.export_formats.split(",")) if policy else {"csv", "json", "pdf", "zip"}
    invalid = [fmt for fmt in payload.formats if fmt not in allowed_formats]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unsupported export formats: {', '.join(invalid)}")
    job = DataExportJob(
        tenant_id=resolved_tenant,
        requested_by=current_user.id,
        export_type=payload.export_type,
        status="completed",
        formats=",".join(payload.formats),
        requested_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        storage_uri=f"s3://tenant-{resolved_tenant}/exports/{payload.export_type}-{datetime.utcnow().isoformat()}",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return DataExportJobRead.from_orm(job)
