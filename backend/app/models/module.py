# backend/app/models/module.py
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base_class import Base
from app.db.json_compat import JSONCompatible
from app.models.base import TimestampMixin, ModelMixin


class ModuleStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


_DISABLED_STATUSES = {
    ModuleStatus.DISABLED,
    ModuleStatus.DEPRECATED,
    ModuleStatus.RETIRED,
}


class Module(Base, TimestampMixin, ModelMixin):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(64), unique=True, nullable=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100))
    phase = Column(Integer, nullable=True)
    impact_level = Column(String(50), nullable=True)
    path = Column(String(255), nullable=True)
    status = Column(
        SQLEnum(
            ModuleStatus,
            name="module_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=ModuleStatus.ACTIVE.value,
        server_default=ModuleStatus.ACTIVE.value,
    )
    checksum = Column(String(128), nullable=True)
    description = Column(Text)
    purpose = Column(Text, nullable=True)
    dependencies = Column(Text, nullable=True)
    preconditions = Column(Text, nullable=True)
    team = Column(String(150), nullable=True)
    operating_systems = Column(String(255), nullable=True)
    application_target = Column(String(255), nullable=True)
    compliance_mapping = Column(Text, nullable=True)
    parameter_schema = Column(JSONB, nullable=True)
    last_update = Column(DateTime, nullable=True)
    enabled = Column(Boolean, nullable=False, default=False, server_default=expression.false())

    tenant_modules = relationship("TenantModule", back_populates="module")
    scan_results = relationship("ScanModuleResult", back_populates="module", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint("name", name="uq_module_name"),
    )

    @property
    def is_effectively_enabled(self) -> bool:
        """Return True when the module is enabled and not marked as disabled by status."""
        raw = self.status.value if isinstance(self.status, ModuleStatus) else self.status
        try:
            status = ModuleStatus(raw)
        except Exception:
            status = ModuleStatus.ACTIVE
        base_flag = getattr(self, "enabled", None)
        base_enabled = True if base_flag is None else bool(base_flag)
        return base_enabled and status not in _DISABLED_STATUSES
