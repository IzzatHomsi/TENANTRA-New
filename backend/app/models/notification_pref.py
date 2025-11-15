from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import ModelMixin, TimestampMixin




class NotificationPreference(Base, TimestampMixin, ModelMixin):
    """Per-tenant and optional per-user notification preferences.

    When user_id is NULL, the row defines tenant-wide defaults.
    A user-specific row overrides tenant defaults for that user.
    """

    __tablename__ = "notification_prefs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Enabled channels and events stored as JSON objects
    channels = Column(MutableDict.as_mutable(JSONB), nullable=False, default=dict)  # e.g., {"email": true, "webhook": false}
    events = Column(MutableDict.as_mutable(JSONB), nullable=False, default=dict)    # e.g., {"scan_failed": true, ...}
    digest = Column(String(32), nullable=False, default="immediate")  # immediate|hourly|daily

    tenant = relationship("Tenant")
    user = relationship("User")
