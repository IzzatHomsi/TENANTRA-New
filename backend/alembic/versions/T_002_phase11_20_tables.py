"""Phase 11-20 feature tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "T_002_phase11_20_tables"
down_revision = "T_001_add_tenants_and_fk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("agents"):
        op.create_table(
            "agents",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("os", sa.String(length=128), nullable=True),
            sa.Column("version", sa.String(length=64), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text('\'active\'')),
            sa.Column("last_seen_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_agents_tenant_id", "agents", ["tenant_id"])
        op.create_index("ix_agents_name", "agents", ["name"])

    if not insp.has_table("assets"):
        op.create_table(
            "assets",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("os", sa.String(length=100), nullable=True),
            sa.Column("hostname", sa.String(length=255), nullable=True),
            sa.Column("last_seen", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_assets_tenant_id", "assets", ["tenant_id"])
        op.create_index("ix_assets_hostname", "assets", ["hostname"])
        op.create_index("ix_assets_ip_address", "assets", ["ip_address"])

    if not insp.has_table("notifications"):
        op.create_table(
            "notifications",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text('\'pending\'')),
            sa.Column("severity", sa.String(length=50), nullable=True),
            sa.Column("sent_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "title", "created_at", name="uq_notifications_tenant_title_created_at"),
        )
        op.create_index("ix_notifications_tenant_id", "notifications", ["tenant_id"])
        op.create_index("ix_notifications_recipient_id", "notifications", ["recipient_id"])
        op.create_index("ix_notifications_status", "notifications", ["status"])

    op.create_table(
        "registry_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hive", sa.String(length=128), nullable=False),
        sa.Column("key_path", sa.String(length=512), nullable=False),
        sa.Column("value_name", sa.String(length=256), nullable=True),
        sa.Column("value_data", sa.Text(), nullable=True),
        sa.Column("value_type", sa.String(length=64), nullable=True),
        sa.Column("collected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("agent_id", "hive", "key_path", "value_name", "collected_at", name="uq_registry_snapshot_identity"),
    )

    op.create_table(
        "boot_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False),
        sa.Column("config_path", sa.String(length=512), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("collected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "integrity_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="medium"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("reference_type", sa.String(length=64), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "service_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("start_mode", sa.String(length=64), nullable=True),
        sa.Column("run_account", sa.String(length=255), nullable=True),
        sa.Column("binary_path", sa.Text(), nullable=True),
        sa.Column("hash", sa.String(length=128), nullable=True),
        sa.Column("collected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "task_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("schedule", sa.String(length=255), nullable=True),
        sa.Column("command", sa.Text(), nullable=False),
        sa.Column("last_run_time", sa.DateTime(), nullable=True),
        sa.Column("next_run_time", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("collected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "ioc_feeds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("feed_type", sa.String(length=64), nullable=False, server_default="indicator"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=512), nullable=True),
        sa.Column("api_key_name", sa.String(length=128), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "ioc_hits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feed_id", sa.Integer(), sa.ForeignKey("ioc_feeds.id", ondelete="CASCADE"), nullable=False),
        sa.Column("indicator_type", sa.String(length=64), nullable=False),
        sa.Column("indicator_value", sa.String(length=512), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_identifier", sa.String(length=255), nullable=True),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="medium"),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "compliance_frameworks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "compliance_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("control_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("service_area", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "compliance_rule_frameworks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_id", sa.Integer(), sa.ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("framework_id", sa.Integer(), sa.ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reference", sa.String(length=128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "tenant_retention_policies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("retention_days", sa.Integer(), nullable=False, server_default="90"),
        sa.Column("archive_storage", sa.String(length=128), nullable=True),
        sa.Column("export_formats", sa.String(length=128), nullable=False, server_default="csv,json,pdf,zip"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "data_export_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("export_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("formats", sa.String(length=128), nullable=False),
        sa.Column("storage_uri", sa.String(length=512), nullable=True),
        sa.Column("requested_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "billing_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("currency", sa.String(length=16), nullable=False, server_default="USD"),
        sa.Column("base_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("overage_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "usage_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric", sa.String(length=128), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("window_start", sa.DateTime(), nullable=True),
        sa.Column("window_end", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("billing_plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("period_start", sa.DateTime(), nullable=False),
        sa.Column("period_end", sa.DateTime(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=False, server_default="USD"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("issued_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("scan_type", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False, server_default="normal"),
        sa.Column("schedule", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "scan_results_v2",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("scan_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notification_id", sa.Integer(), sa.ForeignKey("notifications.id", ondelete="SET NULL"), nullable=True),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="sent"),
        sa.Column("sent_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("error", sa.Text(), nullable=True),
    )

    op.create_table(
        "cloud_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("account_identifier", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("credential_reference", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "cloud_assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("cloud_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=128), nullable=False),
        sa.Column("region", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("discovered_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("cloud_assets")
    op.drop_table("cloud_accounts")
    op.drop_table("notification_logs")
    op.drop_table("scan_results_v2")
    op.drop_table("scan_jobs")
    op.drop_table("invoices")
    op.drop_table("usage_logs")
    op.drop_table("billing_plans")
    op.drop_table("data_export_jobs")
    op.drop_table("tenant_retention_policies")
    op.drop_table("compliance_rule_frameworks")
    op.drop_table("compliance_rules")
    op.drop_table("compliance_frameworks")
    op.drop_table("ioc_hits")
    op.drop_table("ioc_feeds")
    op.drop_table("task_snapshots")
    op.drop_table("service_snapshots")
    op.drop_table("integrity_events")
    op.drop_table("boot_configs")
    op.drop_table("registry_snapshots")


