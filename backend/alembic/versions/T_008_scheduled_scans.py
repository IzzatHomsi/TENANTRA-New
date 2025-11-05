
"""Create scheduled_scans table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "T_008_scheduled_scans"
down_revision = "T_007_platform_foundations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scheduled_scans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("modules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cron_expr", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="scheduled"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_scheduled_scans_tenant", "scheduled_scans", ["tenant_id"])
    op.create_index("ix_scheduled_scans_module", "scheduled_scans", ["module_id"])
    op.create_index("ix_scheduled_scans_agent", "scheduled_scans", ["agent_id"])


def downgrade() -> None:
    op.drop_index("ix_scheduled_scans_agent", table_name="scheduled_scans")
    op.drop_index("ix_scheduled_scans_module", table_name="scheduled_scans")
    op.drop_index("ix_scheduled_scans_tenant", table_name="scheduled_scans")
    op.drop_table("scheduled_scans")
