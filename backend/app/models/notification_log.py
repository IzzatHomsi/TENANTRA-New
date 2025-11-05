from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class NotificationLog(Base):
    """Historical record of notifications delivered to users/tenants."""

    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    notification_id = Column(Integer, ForeignKey("notifications.id", ondelete="SET NULL"), nullable=True)
    channel = Column(String(64), nullable=False)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    error = Column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="notification_logs")
    notification = relationship("Notification", backref="history")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "notification_id": self.notification_id,
            "channel": self.channel,
            "recipient": self.recipient,
            "subject": self.subject,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error": self.error,
        }
