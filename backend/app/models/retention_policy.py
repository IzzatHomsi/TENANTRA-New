from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class TenantRetentionPolicy(Base, TimestampMixin, ModelMixin):
    """Retention configuration per tenant."""

    __tablename__ = "tenant_retention_policies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True)
    retention_days = Column(Integer, nullable=False, default=90)
    archive_storage = Column(String(128), nullable=True)
    export_formats = Column(String(128), nullable=False, default="csv,json,pdf,zip")

    tenant = relationship("Tenant", back_populates="retention_policy")

    def as_dict(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "retention_days": self.retention_days,
            "archive_storage": self.archive_storage,
            "export_formats": self.export_formats.split(",") if self.export_formats else [],
        }



