from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class ServiceSnapshot(Base, TimestampMixin, ModelMixin):
    """Represents the runtime configuration of a service recorded at a point in time."""

    __tablename__ = "service_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    status = Column(String(64), nullable=False)
    start_mode = Column(String(64), nullable=True)
    run_account = Column(String(255), nullable=True)
    binary_path = Column(Text, nullable=True)
    hash = Column(String(128), nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="service_snapshots")
    agent = relationship("Agent", back_populates="service_snapshots")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "name": self.name,
            "display_name": self.display_name,
            "status": self.status,
            "start_mode": self.start_mode,
            "run_account": self.run_account,
            "binary_path": self.binary_path,
            "hash": self.hash,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
        }
