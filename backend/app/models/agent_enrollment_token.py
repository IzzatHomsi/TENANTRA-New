from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class AgentEnrollmentToken(Base, TimestampMixin, ModelMixin):
    __tablename__ = "agent_enrollment_tokens"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(128), nullable=False, unique=True)
    label = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    __table_args__ = (
        Index("ix_agent_enrollment_tokens_expires_at", "expires_at"),
        Index("ix_agent_enrollment_tokens_tenant", "tenant_id"),
    )
