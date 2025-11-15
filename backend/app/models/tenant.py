from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin
from app.models.asset import Asset
from app.models.user import User
from app.models.notification import Notification
from app.models.tenant_module import TenantModule
from app.models.compliance_result import ComplianceResult
from app.models.agent import Agent
# Ensure dependent classes are imported so string-based relationship targets resolve
from app.models.process_snapshot import ProcessSnapshot
from app.models.process_baseline import ProcessBaseline
from app.models.process_drift_event import ProcessDriftEvent
from app.models.registry_snapshot import RegistrySnapshot
from app.models.boot_config import BootConfig
from app.models.integrity_event import IntegrityEvent
from app.models.service_snapshot import ServiceSnapshot
from app.models.task_snapshot import TaskSnapshot
from app.models.retention_policy import TenantRetentionPolicy
from app.models.data_export import DataExportJob
from app.models.compliance_report import ComplianceReport
from app.models.billing_plan import Invoice, UsageLog
from app.models.ioc_hit import IOCHit
from app.models.scan_job import ScanJob
from app.models.notification_log import NotificationLog
from app.models.cloud_account import CloudAccount
from app.models.alert_rule import AlertRule


class Tenant(Base, TimestampMixin, ModelMixin):
    """
    Represents an organization or customer (tenant) using the Tenantra platform.
    """
    __tablename__ = "tenants"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for the tenant"
    )
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Unique tenant name"
    )
    slug = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="URL-safe unique tenant slug"
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="True if tenant is active"
    )
    storage_quota_gb = Column(
        Integer,
        nullable=False,
        default=10,
        comment="Storage quota in GB"
    )

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    join_requests = relationship("TenantJoinRequest", back_populates="tenant", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="tenant", cascade="all, delete-orphan")
    tenant_modules = relationship("TenantModule", back_populates="tenant", cascade="all, delete-orphan")
    compliance_results = relationship("ComplianceResult", back_populates="tenant", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="tenant", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="tenant", cascade="all, delete-orphan")
    process_snapshots = relationship("ProcessSnapshot", back_populates="tenant", cascade="all, delete-orphan")
    process_baselines = relationship("ProcessBaseline", back_populates="tenant", cascade="all, delete-orphan")
    process_drift_events = relationship("ProcessDriftEvent", back_populates="tenant", cascade="all, delete-orphan")
    registry_snapshots = relationship("RegistrySnapshot", back_populates="tenant", cascade="all, delete-orphan")
    boot_configs = relationship("BootConfig", back_populates="tenant", cascade="all, delete-orphan")
    integrity_events = relationship("IntegrityEvent", back_populates="tenant", cascade="all, delete-orphan")
    service_snapshots = relationship("ServiceSnapshot", back_populates="tenant", cascade="all, delete-orphan")
    task_snapshots = relationship("TaskSnapshot", back_populates="tenant", cascade="all, delete-orphan")
    ioc_hits = relationship("IOCHit", back_populates="tenant", cascade="all, delete-orphan")
    retention_policy = relationship("TenantRetentionPolicy", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    data_exports = relationship("DataExportJob", back_populates="tenant", cascade="all, delete-orphan")
    compliance_reports = relationship("ComplianceReport", back_populates="tenant", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="tenant", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="tenant", cascade="all, delete-orphan")
    scan_jobs = relationship("ScanJob", back_populates="tenant", cascade="all, delete-orphan")
    notification_logs = relationship("NotificationLog", back_populates="tenant", cascade="all, delete-orphan")
    cloud_accounts = relationship("CloudAccount", back_populates="tenant", cascade="all, delete-orphan")
    alert_rules = relationship("AlertRule", back_populates="tenant", cascade="all, delete-orphan")
