"""Service baselines table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "T_016_service_baselines"
down_revision = "T_015_integrity_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_baselines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("expected_status", sa.String(length=64), nullable=True),
        sa.Column("expected_start_mode", sa.String(length=64), nullable=True),
        sa.Column("expected_hash", sa.String(length=128), nullable=True),
        sa.Column("expected_run_account", sa.String(length=255), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "agent_id", "name", name="uq_service_baseline_identity"),
    )
    op.create_index("ix_service_baselines_tenant", "service_baselines", ["tenant_id", "agent_id"])


def downgrade() -> None:
    try:
        op.drop_index("ix_service_baselines_tenant", table_name="service_baselines")
    except Exception:
        pass
    op.drop_table("service_baselines")
