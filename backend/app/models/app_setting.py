from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class AppSetting(Base, TimestampMixin, ModelMixin):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    key = Column(String(255), nullable=False)
    value = Column(JSONB, nullable=True)

    tenant = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_app_settings_scope_key"),
    )
