from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class IOCHit(Base, TimestampMixin, ModelMixin):
    """Association of a tenant asset/entity with an indicator of compromise."""

    __tablename__ = "ioc_hits"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    feed_id = Column(Integer, ForeignKey("ioc_feeds.id", ondelete="CASCADE"), nullable=False, index=True)
    indicator_type = Column(String(64), nullable=False)
    indicator_value = Column(String(512), nullable=False)
    entity_type = Column(String(64), nullable=False)
    entity_identifier = Column(String(255), nullable=True)
    severity = Column(String(32), nullable=False, default="medium")
    context = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    feed = relationship("IOCFeed", back_populates="hits")
    tenant = relationship("Tenant", back_populates="ioc_hits")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "feed_id": self.feed_id,
            "indicator_type": self.indicator_type,
            "indicator_value": self.indicator_value,
            "entity_type": self.entity_type,
            "entity_identifier": self.entity_identifier,
            "severity": self.severity,
            "context": self.context,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }
