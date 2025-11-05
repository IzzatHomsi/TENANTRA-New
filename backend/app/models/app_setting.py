from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from app.db.json_compat import JSONCompatible
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    key = Column(String(255), nullable=False)
    value = Column(JSONCompatible(), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_app_settings_scope_key"),
    )
