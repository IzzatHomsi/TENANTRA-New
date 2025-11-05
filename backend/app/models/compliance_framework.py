from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ComplianceFramework(Base):
    """Represents a security/compliance framework (e.g., ISO27001, NIST)."""

    __tablename__ = "compliance_frameworks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    rules = relationship("ComplianceRule", secondary="compliance_rule_frameworks", back_populates="frameworks")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "category": self.category,
        }
