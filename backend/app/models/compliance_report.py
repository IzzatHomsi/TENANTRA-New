from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class ComplianceReport(Base, TimestampMixin, ModelMixin):
    """Represents a generated compliance report."""

    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    file_path = Column(String(512), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    tenant = relationship("Tenant", back_populates="compliance_reports")
    generator = relationship("User", backref="generated_compliance_reports")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "report_type": self.report_type,
            "status": self.status,
            "file_path": self.file_path,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "generated_by": self.generated_by,
        }
