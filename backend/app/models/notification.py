"""Notification ORM model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class Notification(Base, TimestampMixin, ModelMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    recipient_email = Column(String(255), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=True)
    sent_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="notifications", lazy="joined")
    recipient = relationship("User", lazy="joined")