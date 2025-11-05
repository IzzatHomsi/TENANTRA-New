from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import backref, relationship

from app.db.base_class import Base


class ComplianceRule(Base):
    """Represents a Tenantra control that maps to one or more frameworks."""

    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(128), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(128), nullable=True)
    service_area = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    frameworks = relationship(
        "ComplianceFramework",
        secondary="compliance_rule_frameworks",
        back_populates="rules",
    )

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "control_id": self.control_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "service_area": self.service_area,
            "framework_codes": [f.code for f in self.frameworks],
        }


class ComplianceRuleFramework(Base):
    """Association table linking compliance rules to frameworks with metadata."""

    __tablename__ = "compliance_rule_frameworks"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), nullable=False)
    reference = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    rule = relationship(
        "ComplianceRule",
        backref=backref("framework_links", overlaps="frameworks,rules"),
        overlaps="frameworks,rules",
    )
    framework = relationship(
        "ComplianceFramework",
        backref=backref("rule_links", overlaps="frameworks,rules"),
        overlaps="frameworks,rules",
    )

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "framework_id": self.framework_id,
            "reference": self.reference,
            "notes": self.notes,
        }
