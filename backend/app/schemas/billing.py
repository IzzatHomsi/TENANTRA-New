from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BillingPlanBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    currency: str = "USD"
    base_rate: float = Field(0, ge=0)
    overage_rate: float = Field(0, ge=0)


class BillingPlanCreate(BillingPlanBase):
    pass


class BillingPlanRead(BillingPlanBase):
    id: int

    class Config:
        orm_mode = True


class UsageLogRead(BaseModel):
    id: int
    tenant_id: int
    metric: str
    quantity: float
    recorded_at: datetime
    window_start: Optional[datetime]
    window_end: Optional[datetime]

    class Config:
        orm_mode = True


class UsageLogCreate(BaseModel):
    metric: str
    quantity: float
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None


class InvoiceCreate(BaseModel):
    plan_id: Optional[int] = None
    period_start: datetime
    period_end: datetime
    amount: float
    currency: str = "USD"
    notes: Optional[str] = None


class InvoiceRead(InvoiceCreate):
    id: int
    tenant_id: int
    status: str
    issued_at: datetime
    due_at: Optional[datetime]
    paid_at: Optional[datetime]

    class Config:
        orm_mode = True
