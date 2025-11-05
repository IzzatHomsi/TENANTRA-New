"""Registry and task baselines tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "T_017_registry_task_baselines"
down_revision = "T_016_service_baselines"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "registry_baselines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("hive", sa.String(length=128), nullable=False),
        sa.Column("key_path", sa.String(length=512), nullable=False),
        sa.Column("value_name", sa.String(length=256), nullable=True),
        sa.Column("expected_value", sa.Text(), nullable=True),
        sa.Column("expected_type", sa.String(length=64), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "agent_id", "hive", "key_path", "value_name", name="uq_registry_baseline_identity"),
    )
    op.create_index("ix_registry_baselines_tenant", "registry_baselines", ["tenant_id", "agent_id"])

    op.create_table(
        "task_baselines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("expected_schedule", sa.String(length=255), nullable=True),
        sa.Column("expected_command", sa.Text(), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "agent_id", "name", name="uq_task_baseline_identity"),
    )
    op.create_index("ix_task_baselines_tenant", "task_baselines", ["tenant_id", "agent_id"])


def downgrade() -> None:
    try:
        op.drop_index("ix_task_baselines_tenant", table_name="task_baselines")
    except Exception:
        pass
    op.drop_table("task_baselines")
    try:
        op.drop_index("ix_registry_baselines_tenant", table_name="registry_baselines")
    except Exception:
        pass
    op.drop_table("registry_baselines")

