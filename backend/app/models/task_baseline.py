from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TaskBaseline(Base):
    __tablename__ = "task_baselines"
    __table_args__ = (
        UniqueConstraint("tenant_id", "agent_id", "name", name="uq_task_baseline_identity"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    task_type = Column(String(64), nullable=False)
    expected_schedule = Column(String(255), nullable=True)
    expected_command = Column(Text, nullable=True)
    is_critical = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant")
    agent = relationship("Agent")

