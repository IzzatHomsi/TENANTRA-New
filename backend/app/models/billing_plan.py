from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class BillingPlan(Base, TimestampMixin, ModelMixin):
    """Defines available billing plans for MSP tenants."""

    __tablename__ = "billing_plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    currency = Column(String(16), nullable=False, default="USD")
    base_rate = Column(Float, nullable=False, default=0.0)
    overage_rate = Column(Float, nullable=False, default=0.0)

    invoices = relationship("Invoice", back_populates="plan")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "currency": self.currency,
            "base_rate": self.base_rate,
            "overage_rate": self.overage_rate,
        }


class UsageLog(Base, TimestampMixin, ModelMixin):
    """Usage metrics recorded per tenant for billing purposes."""

    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    metric = Column(String(128), nullable=False)
    quantity = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    window_start = Column(DateTime, nullable=True)
    window_end = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="usage_logs")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "metric": self.metric,
            "quantity": self.quantity,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "window_start": self.window_start.isoformat() if self.window_start else None,
            "window_end": self.window_end.isoformat() if self.window_end else None,
        }


class Invoice(Base, TimestampMixin, ModelMixin):
    """Invoices generated for tenants."""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("billing_plans.id", ondelete="SET NULL"), nullable=True, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(16), nullable=False, default="USD")
    status = Column(String(32), nullable=False, default="pending")
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    plan = relationship("BillingPlan", back_populates="invoices")
    tenant = relationship("Tenant", back_populates="invoices")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "plan_id": self.plan_id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "notes": self.notes,
        }
