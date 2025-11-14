# backend/app/models/__init__.py
# PURPOSE:
# - Ensure all model classes are imported after Base exists so SQLAlchemy
#   registers them properly.
# - IMPORTANT: Import Base ONLY from app.db.base_class (NOT from app.db).
# - DO NOT import app.db here (prevents circular import).

from app.db.base_class import Base  # Base first, then model modules

# List all models so that Alembic sees them in metadata:
# (Adjust to your actual project models; keep one-way imports)
from .user import User  # noqa: F401
from .role import Role  # noqa: F401
from .tenant import Tenant  # noqa: F401
from .audit_log import AuditLog  # noqa: F401

# Phase 3-8 & platform models (extend this list to match your repo)
try:
    from .notification import Notification  # noqa: F401
except Exception:
    pass
try:
    from .app_setting import AppSetting  # noqa: F401
except Exception:
    pass
try:
    from .alert_rule import AlertRule  # noqa: F401
except Exception:
    pass
try:
    from .compliance_result import ComplianceResult  # noqa: F401
except Exception:
    pass
try:
    from .asset import Asset  # noqa: F401
except Exception:
    pass
try:
    from .agent import Agent  # noqa: F401
except Exception:
    pass
try:
    from .scheduled_scan import ScheduledScan  # noqa: F401
except Exception:
    pass
try:
    from .module import Module  # noqa: F401
    from .module_agent_mapping import ModuleAgentMapping  # noqa: F401
except Exception:
    pass
try:
    from .scan_module_result import ScanModuleResult  # noqa: F401
except Exception:
    pass
try:
    from .scan_job import ScanJob, ScanResult  # noqa: F401
except Exception:
    pass
try:
    from .file_visibility_result import FileVisibilityResult  # noqa: F401
    from .network_visibility_result import NetworkVisibilityResult  # noqa: F401
except Exception:
    pass
try:
    from .tenant_module import TenantModule  # noqa: F401
except Exception:
    pass
try:
    from .file_scan_result import FileScanResult  # noqa: F401
except Exception:
    pass
try:
    from .agent_log import AgentLog  # noqa: F401
except Exception:
    pass
try:
    from .refresh_token import RefreshToken  # noqa: F401
except Exception:
    pass
try:
    from .password_reset_token import PasswordResetToken  # noqa: F401
    from .revoked_token import RevokedToken  # noqa: F401
except Exception:
    pass
try:
    from .agent_enrollment_token import AgentEnrollmentToken  # noqa: F401
except Exception:
    pass
try:
    from .scan_job import ScanJob, ScanResult  # noqa: F401
except Exception:
    pass
try:
    from .registry_snapshot import RegistrySnapshot  # noqa: F401
    from .boot_config import BootConfig  # noqa: F401
    from .integrity_event import IntegrityEvent  # noqa: F401
    from .service_snapshot import ServiceSnapshot  # noqa: F401
    from .task_snapshot import TaskSnapshot  # noqa: F401
    from .process_snapshot import ProcessSnapshot  # noqa: F401
    from .process_baseline import ProcessBaseline  # noqa: F401
    from .process_drift_event import ProcessDriftEvent  # noqa: F401
    from .ioc_feed import IOCFeed  # noqa: F401
    from .ioc_hit import IOCHit  # noqa: F401
    from .compliance_framework import ComplianceFramework  # noqa: F401
    from .compliance_rule import ComplianceRule, ComplianceRuleFramework  # noqa: F401
    from .retention_policy import TenantRetentionPolicy, DataExportJob  # noqa: F401
    from .billing_plan import BillingPlan, UsageLog, Invoice  # noqa: F401
    from .notification_log import NotificationLog  # noqa: F401
    from .cloud_account import CloudAccount, CloudAsset  # noqa: F401
    from .service_baseline import ServiceBaseline  # noqa: F401
    from .registry_baseline import RegistryBaseline  # noqa: F401
    from .task_baseline import TaskBaseline  # noqa: F401
except Exception:
    pass

__all__ = [
    "Base",
    "User",
    "Role",
    "Tenant",
    "AuditLog",
    # The rest are imported dynamically above if present.
]
