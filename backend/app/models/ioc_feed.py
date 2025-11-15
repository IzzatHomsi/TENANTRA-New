from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class IOCFeed(Base, TimestampMixin, ModelMixin):
    """Threat intelligence feed metadata and ingestion status."""

    __tablename__ = "ioc_feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    source = Column(String(255), nullable=True)
    feed_type = Column(String(64), nullable=False, default="indicator")
    description = Column(Text, nullable=True)
    url = Column(String(512), nullable=True)
    api_key_name = Column(String(128), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    last_synced_at = Column(DateTime, nullable=True)

    hits = relationship("IOCHit", back_populates="feed", cascade="all, delete-orphan")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "feed_type": self.feed_type,
            "description": self.description,
            "url": self.url,
            "enabled": self.enabled,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
        }
