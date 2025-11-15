from __future__ import annotations

import datetime
import json
import logging
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.core.crypto import decrypt_data, encrypt_data
from app.core.secrets import get_enc_key
from app.db import Base
from app.models.base import TimestampMixin, ModelMixin

logger = logging.getLogger(__name__)


class AuditLog(Base, TimestampMixin, ModelMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_result", "result"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=True)
    result = Column(String(50), nullable=True)
    ip = Column(String(45), nullable=True)
    details_enc = Column("details", String)

    user = relationship("User", back_populates="audit_logs")

    @property
    def details(self) -> Optional[Dict[str, Any]]:
        if not self.details_enc:
            return None
        try:
            decrypted = decrypt_data(self.details_enc, get_enc_key())
            return json.loads(decrypted) if decrypted else None
        except Exception:
            logger.warning("Failed to decrypt and parse audit log details for log_id=%s", self.id, exc_info=True)
            return None

    @details.setter
    def details(self, value: Optional[str]) -> None:
        self.details_enc = encrypt_data(value, get_enc_key()) if value else None

