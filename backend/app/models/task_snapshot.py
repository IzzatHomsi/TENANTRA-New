from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class TaskSnapshot(Base, TimestampMixin, ModelMixin):
    """Represents a scheduled task or cron entry at a specific point in time."""

    __tablename__ = "task_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    task_type = Column(String(64), nullable=False)
    schedule = Column(String(255), nullable=True)
    command = Column(Text, nullable=False)
    last_run_time = Column(DateTime, nullable=True)
    next_run_time = Column(DateTime, nullable=True)
    status = Column(String(64), nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="task_snapshots")
    agent = relationship("Agent", back_populates="task_snapshots")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "name": self.name,
            "task_type": self.task_type,
            "schedule": self.schedule,
            "command": self.command,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "next_run_time": self.next_run_time.isoformat() if self.next_run_time else None,
            "status": self.status,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
        }
