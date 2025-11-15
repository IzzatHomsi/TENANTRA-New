from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.tenant import Tenant
from app.models.tenant_join_request import TenantJoinRequest
from app.models.user import User
from app.services import email_service
from app.utils.audit import log_audit_event

ADMIN_ROLES = ("admin", "super_admin", "owner")

router = APIRouter(prefix="", tags=["Tenant Join Requests"])


class TenantLookupOut(BaseModel):
    id: int
    name: str
    slug: str


class TenantJoinRequestCreate(BaseModel):
    tenant_identifier: str = Field(..., min_length=1, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    message: Optional[str] = Field(None, max_length=1000)


class TenantJoinRequestDecision(BaseModel):
    decision: Literal["approved", "denied"]
    note: Optional[str] = Field(None, max_length=1000)


def _serialize_join_request(data: TenantJoinRequest) -> dict:
    return {
        "id": data.id,
        "tenant_id": data.tenant_id,
        "full_name": data.full_name,
        "email": data.email,
        "message": data.message,
        "status": data.status,
        "decision_note": data.decision_note,
        "decision_at": data.decision_at.isoformat() if data.decision_at else None,
        "decision_by": data.decision_by,
        "created_at": data.created_at.isoformat() if data.created_at else None,
        "updated_at": data.updated_at.isoformat() if data.updated_at else None,
    }


def _resolve_tenant(db: Session, identifier: str) -> Optional[Tenant]:
    if identifier.isdigit():
        tenant = db.query(Tenant).filter(Tenant.id == int(identifier)).first()
        if tenant:
            return tenant
    return (
        db.query(Tenant)
        .filter(func.lower(Tenant.slug) == identifier.lower())
        .first()
    )


@router.get("/tenants/search", response_model=List[TenantLookupOut])
def search_tenants(
    q: str = Query(..., min_length=2, max_length=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Tenant)
        .filter(Tenant.is_active.is_(True))
        .filter(
            func.lower(Tenant.name).like(f"%{q.lower()}%")
            | func.lower(Tenant.slug).like(f"%{q.lower()}%")
        )
        .order_by(Tenant.name.asc())
        .limit(10)
    )
    return [TenantLookupOut(id=row.id, name=row.name, slug=row.slug) for row in query]


@router.post("/tenants/join-requests", status_code=status.HTTP_202_ACCEPTED)
def create_join_request(
    payload: TenantJoinRequestCreate,
    db: Session = Depends(get_db),
):
    tenant = _resolve_tenant(db, payload.tenant_identifier)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    existing = (
        db.query(TenantJoinRequest)
        .filter(
            TenantJoinRequest.tenant_id == tenant.id,
            func.lower(TenantJoinRequest.email) == payload.email.lower(),
            TenantJoinRequest.status == "pending",
        )
        .first()
    )
    if existing:
        return {"status": "pending"}

    request_obj = TenantJoinRequest(
        tenant_id=tenant.id,
        full_name=payload.full_name,
        email=payload.email,
        message=payload.message,
        status="pending",
    )
    db.add(request_obj)
    db.commit()
    db.refresh(request_obj)

    admin_emails = [
        u.email
        for u in db.query(User)
        .filter(
            User.tenant_id == tenant.id,
            func.lower(User.role).in_(ADMIN_ROLES),
        )
        .all()
        if u.email
    ]
    try:
        email_service.notify_join_request_submitted(request_obj, tenant, admin_emails)
    except Exception:
        pass
    try:
        email_service.acknowledge_join_request(request_obj, tenant)
    except Exception:
        pass

    return {"status": "submitted"}


@router.get("/admin/tenant-join-requests")
def list_join_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    query = (
        db.query(TenantJoinRequest)
        .filter(TenantJoinRequest.tenant_id == current_user.tenant_id)
        .order_by(TenantJoinRequest.created_at.desc())
        .limit(200)
    )
    return [_serialize_join_request(row) for row in query]


@router.post("/admin/tenant-join-requests/{request_id}/decision")
def decide_join_request(
    request_id: int,
    payload: TenantJoinRequestDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    record = (
        db.query(TenantJoinRequest)
        .filter(
            TenantJoinRequest.id == request_id,
            TenantJoinRequest.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Join request not found")
    if record.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")

    record.status = payload.decision
    record.decision_note = payload.note
    record.decision_at = datetime.utcnow()
    record.decision_by = current_user.id
    db.add(record)
    db.commit()
    db.refresh(record)

    log_audit_event(
        db,
        user_id=current_user.id,
        action=f"tenant_join_request.{payload.decision}",
        result="success",
        details={"request_id": record.id},
    )
    try:
        email_service.notify_join_request_decision(record)
    except Exception:
        pass

    return _serialize_join_request(record)
