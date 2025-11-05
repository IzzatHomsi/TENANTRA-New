"""Phase 10 process visibility tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "T_003_phase10_process_tables"
down_revision = "T_002_phase11_20_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "process_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_id", sa.String(length=64), nullable=False),
        sa.Column("process_name", sa.String(length=255), nullable=False),
        sa.Column("pid", sa.Integer(), nullable=False),
        sa.Column("executable_path", sa.Text(), nullable=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("hash", sa.String(length=128), nullable=True),
        sa.Column("command_line", sa.Text(), nullable=True),
        sa.Column("collected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_process_snapshot_agent_time",
        "process_snapshots",
        ["tenant_id", "agent_id", "collected_at"],
    )
    op.create_index("ix_process_snapshot_report", "process_snapshots", ["report_id"])

    op.create_table(
        "process_baselines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("process_name", sa.String(length=255), nullable=False),
        sa.Column("executable_path", sa.Text(), nullable=True),
        sa.Column("expected_hash", sa.String(length=128), nullable=True),
        sa.Column("expected_user", sa.String(length=255), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "tenant_id",
            "agent_id",
            "process_name",
            "executable_path",
            name="uq_process_baseline_identity",
        ),
    )

    op.create_table(
        "process_drift_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("change_type", sa.String(length=64), nullable=False),
        sa.Column("process_name", sa.String(length=255), nullable=False),
        sa.Column("pid", sa.Integer(), nullable=True),
        sa.Column("executable_path", sa.Text(), nullable=True),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="medium"),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_process_drift_detected",
        "process_drift_events",
        ["tenant_id", "agent_id", "detected_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_process_drift_detected", table_name="process_drift_events")
    op.drop_table("process_drift_events")
    op.drop_table("process_baselines")
    op.drop_index("ix_process_snapshot_report", table_name="process_snapshots")
    op.drop_index("ix_process_snapshot_agent_time", table_name="process_snapshots")
    op.drop_table("process_snapshots")
