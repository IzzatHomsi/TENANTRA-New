from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class BootConfig(Base, TimestampMixin, ModelMixin):
    """Bootloader configuration snapshot collected from an endpoint."""

    __tablename__ = "boot_configs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(64), nullable=False)
    config_path = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    checksum = Column(String(128), nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="boot_configs")
    agent = relationship("Agent", back_populates="boot_configs")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "platform": self.platform,
            "config_path": self.config_path,
            "checksum": self.checksum,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
        }
