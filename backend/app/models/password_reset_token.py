from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(128), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    user_agent = Column(String(256), nullable=True)
    ip = Column(String(64), nullable=True)

    user = relationship("User")

    __table_args__ = (
        Index("ix_password_reset_tokens_expires_at", "expires_at"),
    )
