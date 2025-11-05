"""MSP billing and usage management endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.billing_plan import BillingPlan, Invoice, UsageLog
from app.models.user import User
from app.schemas.billing import (
    BillingPlanCreate,
    BillingPlanRead,
    InvoiceCreate,
    InvoiceRead,
    UsageLogCreate,
    UsageLogRead,
)

router = APIRouter(prefix="/billing", tags=["Billing"])


def _ensure_msp(user: User) -> None:
    if user.role not in {"msp_admin", "super_admin", "admin"}:
        raise HTTPException(status_code=403, detail="MSP role required")


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id required")
    return tenant_id


@router.get("/plans", response_model=List[BillingPlanRead])
def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[BillingPlanRead]:
    _ensure_msp(current_user)
    plans = db.query(BillingPlan).order_by(BillingPlan.name.asc()).all()
    return [BillingPlanRead.from_orm(plan) for plan in plans]


@router.post("/plans", response_model=BillingPlanRead, status_code=201)
def create_plan(
    payload: BillingPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingPlanRead:
    _ensure_msp(current_user)
    existing = db.query(BillingPlan).filter(BillingPlan.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Plan code already exists")
    plan = BillingPlan(
        code=payload.code.upper(),
        name=payload.name,
        description=payload.description,
        currency=payload.currency,
        base_rate=payload.base_rate,
        overage_rate=payload.overage_rate,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return BillingPlanRead.from_orm(plan)


@router.get("/usage", response_model=List[UsageLogRead])
def list_usage(
    tenant_id: Optional[int] = Query(None),
    metric: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UsageLogRead]:
    _ensure_msp(current_user)
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    query = db.query(UsageLog).filter(UsageLog.tenant_id == resolved_tenant)
    if metric:
        query = query.filter(UsageLog.metric == metric)
    usage = query.order_by(UsageLog.recorded_at.desc()).limit(limit).all()
    return [UsageLogRead.from_orm(row) for row in usage]


@router.post("/usage", response_model=UsageLogRead, status_code=201)
def create_usage(
    payload: UsageLogCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UsageLogRead:
    _ensure_msp(current_user)
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    log = UsageLog(
        tenant_id=resolved_tenant,
        metric=payload.metric,
        quantity=payload.quantity,
        recorded_at=datetime.utcnow(),
        window_start=payload.window_start,
        window_end=payload.window_end,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return UsageLogRead.from_orm(log)


@router.get("/invoices", response_model=List[InvoiceRead])
def list_invoices(
    tenant_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[InvoiceRead]:
    _ensure_msp(current_user)
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    query = db.query(Invoice).filter(Invoice.tenant_id == resolved_tenant)
    if status:
        query = query.filter(Invoice.status == status)
    invoices = query.order_by(Invoice.period_end.desc()).all()
    return [InvoiceRead.from_orm(inv) for inv in invoices]


@router.post("/invoices", response_model=InvoiceRead, status_code=201)
def create_invoice(
    payload: InvoiceCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceRead:
    _ensure_msp(current_user)
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    invoice = Invoice(
        tenant_id=resolved_tenant,
        plan_id=payload.plan_id,
        period_start=payload.period_start,
        period_end=payload.period_end,
        amount=payload.amount,
        currency=payload.currency,
        notes=payload.notes,
        issued_at=datetime.utcnow(),
        status="pending",
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return InvoiceRead.from_orm(invoice)


@router.post("/invoices/{invoice_id}/pay", response_model=InvoiceRead)
def mark_invoice_paid(
    invoice_id: int = Path(...),
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceRead:
    _ensure_msp(current_user)
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == resolved_tenant)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = "paid"
    invoice.paid_at = datetime.utcnow()
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return InvoiceRead.from_orm(invoice)
