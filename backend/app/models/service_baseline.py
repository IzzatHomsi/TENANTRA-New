from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class ServiceBaseline(Base, TimestampMixin, ModelMixin):
    __tablename__ = "service_baselines"
    __table_args__ = (
        UniqueConstraint("tenant_id", "agent_id", "name", name="uq_service_baseline_identity"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    expected_status = Column(String(64), nullable=True)
    expected_start_mode = Column(String(64), nullable=True)
    expected_hash = Column(String(128) , nullable=True)
    expected_run_account = Column(String(255), nullable=True)
    is_critical = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)

    tenant = relationship("Tenant")
    agent = relationship("Agent")

