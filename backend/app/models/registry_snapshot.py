from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class RegistrySnapshot(Base, TimestampMixin, ModelMixin):
    """Serialized view of a registry key/value pair captured from an endpoint."""

    __tablename__ = "registry_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "hive",
            "key_path",
            "value_name",
            "collected_at",
            name="uq_registry_snapshot_identity",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    hive = Column(String(128), nullable=False)
    key_path = Column(String(512), nullable=False)
    value_name = Column(String(256), nullable=True)
    value_data = Column(Text, nullable=True)
    value_type = Column(String(64), nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    checksum = Column(String(64), nullable=True)

    tenant = relationship("Tenant", back_populates="registry_snapshots")
    agent = relationship("Agent", back_populates="registry_snapshots")
