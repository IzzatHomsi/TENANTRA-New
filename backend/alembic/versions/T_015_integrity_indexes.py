"""Integrity tables indexes for performance"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "T_015_integrity_indexes"
down_revision = "T_014_app_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        op.create_index(
            "ix_registry_tenant_agent_time",
            "registry_snapshots",
            ["tenant_id", "agent_id", "collected_at"],
        )
    except Exception:
        pass
    try:
        op.create_index(
            "ix_registry_hive_key",
            "registry_snapshots",
            ["hive", "key_path"],
        )
    except Exception:
        pass
    try:
        op.create_index(
            "ix_boot_tenant_agent_time",
            "boot_configs",
            ["tenant_id", "agent_id", "collected_at"],
        )
    except Exception:
        pass
    try:
        op.create_index(
            "ix_service_tenant_agent_time",
            "service_snapshots",
            ["tenant_id", "agent_id", "collected_at"],
        )
    except Exception:
        pass
    try:
        op.create_index(
            "ix_service_identity",
            "service_snapshots",
            ["tenant_id", "agent_id", "name"],
        )
    except Exception:
        pass
    try:
        op.create_index(
            "ix_task_tenant_agent_time",
            "task_snapshots",
            ["tenant_id", "agent_id", "collected_at"],
        )
    except Exception:
        pass
    try:
        op.create_index(
            "ix_integrity_detected",
            "integrity_events",
            ["tenant_id", "detected_at"],
        )
    except Exception:
        pass


def downgrade() -> None:
    for name, table in [
        ("ix_integrity_detected", "integrity_events"),
        ("ix_task_tenant_agent_time", "task_snapshots"),
        ("ix_service_identity", "service_snapshots"),
        ("ix_service_tenant_agent_time", "service_snapshots"),
        ("ix_boot_tenant_agent_time", "boot_configs"),
        ("ix_registry_hive_key", "registry_snapshots"),
        ("ix_registry_tenant_agent_time", "registry_snapshots"),
    ]:
        try:
            op.drop_index(name, table_name=table)
        except Exception:
            pass

