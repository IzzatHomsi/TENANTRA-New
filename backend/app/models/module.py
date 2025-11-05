# backend/app/models/module.py
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


_DISABLED_STATUSES = {"disabled", "inactive", "retired", "deprecated"}


class Module(Base, TimestampMixin, ModelMixin):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(64), unique=True, nullable=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100))
    phase = Column(Integer, nullable=True)
    impact_level = Column(String(50), nullable=True)
    path = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    checksum = Column(String(128), nullable=True)
    description = Column(Text)
    purpose = Column(Text, nullable=True)
    dependencies = Column(Text, nullable=True)
    preconditions = Column(Text, nullable=True)
    team = Column(String(150), nullable=True)
    operating_systems = Column(String(255), nullable=True)
    application_target = Column(String(255), nullable=True)
    compliance_mapping = Column(Text, nullable=True)
    parameter_schema = Column(JSON, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    last_update = Column(DateTime, nullable=True)

    tenant_modules = relationship("TenantModule", back_populates="module")
    scan_results = relationship("ScanModuleResult", back_populates="module", cascade="all, delete-orphan")
    scheduled_scans = relationship("ScheduledScan", back_populates="module", passive_deletes=True)
    __table_args__ = (
        UniqueConstraint("name", name="uq_module_name"),
    )

    @property
    def is_effectively_enabled(self) -> bool:
        """Return True when the module is enabled and not marked as disabled by status."""
        status = (self.status or "").strip().lower()
        return bool(self.enabled) and status not in _DISABLED_STATUSES
