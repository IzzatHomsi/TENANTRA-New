from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TenantRetentionPolicy(Base):
    """Retention configuration per tenant."""

    __tablename__ = "tenant_retention_policies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True)
    retention_days = Column(Integer, nullable=False, default=90)
    archive_storage = Column(String(128), nullable=True)
    export_formats = Column(String(128), nullable=False, default="csv,json,pdf,zip")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="retention_policy")

    def as_dict(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "retention_days": self.retention_days,
            "archive_storage": self.archive_storage,
            "export_formats": self.export_formats.split(",") if self.export_formats else [],
        }


class DataExportJob(Base):
    """Represents a user-requested export operation."""

    __tablename__ = "data_export_jobs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    export_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    formats = Column(String(128), nullable=False)
    storage_uri = Column(String(512), nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="data_exports")
    requester = relationship("User", backref="export_jobs")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "requested_by": self.requested_by,
            "export_type": self.export_type,
            "status": self.status,
            "formats": self.formats.split(",") if self.formats else [],
            "storage_uri": self.storage_uri,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
