from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class AlertRule(Base, TimestampMixin, ModelMixin):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    threshold = Column(String, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    tenant = relationship("Tenant", back_populates="alert_rules", lazy="joined")

    def __repr__(self):
        return f"<AlertRule(name={self.name}, condition={self.condition}, enabled={self.enabled})>"
