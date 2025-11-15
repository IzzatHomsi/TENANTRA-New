from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db import Base
from app.models.base import TimestampMixin, ModelMixin

class User(Base, TimestampMixin, ModelMixin):
    """User of the Tenantra platform.

    Inherits TimestampMixin for created/updated timestamps and ModelMixin for repr/as_dict.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    email_verified_at = Column(DateTime, nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    role = Column(String(50), default="standard_user", nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")

    # Refresh tokens (inverse of RefreshToken.user)
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
