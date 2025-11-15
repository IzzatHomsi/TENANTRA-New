from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class EmailVerificationToken(Base, TimestampMixin, ModelMixin):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(128), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    user_agent = Column(String(256), nullable=True)
    ip = Column(String(64), nullable=True)

    user = relationship("User")

    __table_args__ = (
        Index("ix_email_verification_tokens_expires_at", "expires_at"),
    )
