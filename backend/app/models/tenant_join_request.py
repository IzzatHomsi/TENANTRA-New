from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class TenantJoinRequest(Base, TimestampMixin, ModelMixin):
    __tablename__ = "tenant_join_requests"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    decision_note = Column(Text, nullable=True)
    decision_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decision_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="join_requests")
    decided_by = relationship("User")
