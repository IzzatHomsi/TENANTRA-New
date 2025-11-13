from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    jti = Column(String(64), nullable=True, index=True)
    revoked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    reason = Column(String(64), nullable=True)

    user = relationship("User")

    __table_args__ = (
        Index("ix_revoked_tokens_lookup", "user_id", "jti"),
    )
