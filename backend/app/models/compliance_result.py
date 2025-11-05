from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
from app.models.base import TimestampMixin, ModelMixin


class ComplianceResult(Base, TimestampMixin, ModelMixin):
    __tablename__ = "compliance_results"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    module = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    details = Column(String, nullable=True)

    tenant = relationship("Tenant", back_populates="compliance_results")
