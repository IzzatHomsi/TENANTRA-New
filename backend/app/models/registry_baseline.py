from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class RegistryBaseline(Base, TimestampMixin, ModelMixin):
    __tablename__ = "registry_baselines"
    __table_args__ = (
        UniqueConstraint("tenant_id", "agent_id", "hive", "key_path", "value_name", name="uq_registry_baseline_identity"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    hive = Column(String(128), nullable=False)
    key_path = Column(String(512), nullable=False)
    value_name = Column(String(256), nullable=True)
    expected_value = Column(Text, nullable=True)
    expected_type = Column(String(64), nullable=True)
    is_critical = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)

    tenant = relationship("Tenant")
    agent = relationship("Agent")

