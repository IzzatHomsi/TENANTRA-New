"""create scan module results table"""

from alembic import op
import sqlalchemy as sa

revision = "2f6b7a8c9d0e"
down_revision = "1c2e3f4a5b6c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_module_results",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('success', 'failed', 'error', 'skipped')"),
    )
    op.create_index(
        "ix_scan_module_results_module",
        "scan_module_results",
        ["module_id"],
        unique=False,
    )
    op.create_index(
        "ix_scan_module_results_tenant",
        "scan_module_results",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_scan_module_results_tenant", table_name="scan_module_results")
    op.drop_index("ix_scan_module_results_module", table_name="scan_module_results")
    op.drop_table("scan_module_results")