from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class ProcessBaseline(Base, TimestampMixin, ModelMixin):
    """Expected process inventory for a tenant/agent baseline."""

    __tablename__ = "process_baselines"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "agent_id",
            "process_name",
            "executable_path",
            name="uq_process_baseline_identity",
        ),
    )

    id: int = Column(Integer, primary_key=True, index=True)
    tenant_id: int = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Optional[int] = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    process_name: str = Column(String(255), nullable=False)
    executable_path: Optional[str] = Column(Text, nullable=True)
    expected_hash: Optional[str] = Column(String(128), nullable=True)
    expected_user: Optional[str] = Column(String(255), nullable=True)
    is_critical: bool = Column(Boolean, nullable=False, default=False)
    notes: Optional[str] = Column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="process_baselines")
    agent = relationship("Agent", back_populates="process_baselines")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "process_name": self.process_name,
            "executable_path": self.executable_path,
            "expected_hash": self.expected_hash,
            "expected_user": self.expected_user,
            "is_critical": self.is_critical,
            "notes": self.notes,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
