from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class IntegrityEvent(Base, TimestampMixin, ModelMixin):
    """Represents a persistence or integrity drift detected on an endpoint."""

    __tablename__ = "integrity_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    event_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False, default="medium")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(Integer, nullable=True)
    reference_type = Column(String(64), nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="integrity_events")
    agent = relationship("Agent", back_populates="integrity_events")

    # Note: 'metadata' is reserved at class level for SQLAlchemy MetaData; avoid exposing it as a property.
