from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.db.base_class import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class TenantModule(Base):
    __tablename__ = "tenant_modules"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Correct relationships
    tenant = relationship("Tenant", back_populates="tenant_modules")
    module = relationship("Module", back_populates="tenant_modules")  # This line was missing

    __table_args__ = (
        UniqueConstraint('tenant_id', 'module_id', name='uq_tenant_module'),
    )
