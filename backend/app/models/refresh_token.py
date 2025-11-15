from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin

class RefreshToken(Base, TimestampMixin, ModelMixin):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(Text, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip = Column(String(64), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index("ix_refresh_tokens_expires_at", "expires_at"),
    )
