from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.json_compat import JSONCompatible


class ProcessDriftEvent(Base):
    """Represents a change between the current process snapshot and the baseline."""

    __tablename__ = "process_drift_events"
    __table_args__ = (
        Index("ix_process_drift_detected", "tenant_id", "agent_id", "detected_at"),
    )

    id: int = Column(Integer, primary_key=True, index=True)
    tenant_id: int = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    agent_id: Optional[int] = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True)
    change_type: str = Column(String(64), nullable=False)
    process_name: str = Column(String(255), nullable=False)
    pid: Optional[int] = Column(Integer, nullable=True)
    executable_path: Optional[str] = Column(Text, nullable=True)
    old_value = Column(JSONCompatible(), nullable=True)
    new_value = Column(JSONCompatible(), nullable=True)
    severity: str = Column(String(32), nullable=False, default="medium")
    details: Optional[str] = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="process_drift_events")
    agent = relationship("Agent", back_populates="process_drift_events")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "change_type": self.change_type,
            "process_name": self.process_name,
            "pid": self.pid,
            "executable_path": self.executable_path,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "severity": self.severity,
            "details": self.details,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }
