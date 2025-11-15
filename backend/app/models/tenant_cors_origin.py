from datetime import datetime
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin

class TenantCORSOrigin(Base, TimestampMixin, ModelMixin):
    __tablename__ = "tenant_cors_origins"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    origin = Column(Text, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    is_global = Column(Boolean, nullable=False, default=False)

    tenant = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("tenant_id", "origin", name="uq_tenant_origin"),
        Index("ix_tenant_cors_origin", "origin"),
    )
