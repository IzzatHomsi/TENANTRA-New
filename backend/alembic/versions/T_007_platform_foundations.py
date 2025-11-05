
"""Create missing Phase 5-8 tables and agent token column"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = "T_007_platform_foundations"
down_revision = "T_006_audit_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- agents.token -------------------------------------------------------
    op.add_column("agents", sa.Column("token", sa.String(length=64), nullable=True))
    agents_table = table("agents", column("id", sa.Integer), column("token", sa.String(length=64)))
    bind = op.get_bind()
    rows = list(bind.execute(sa.select(agents_table.c.id)))
    for row in rows:
        token = f"legacy-{row.id:08x}"
        bind.execute(
            agents_table.update().where(agents_table.c.id == row.id).values(token=token)
        )
    op.alter_column("agents", "token", nullable=False)
    op.create_index("ix_agents_token", "agents", ["token"], unique=True)

    # --- modules ------------------------------------------------------------
    op.create_table(
        "modules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_module_name"),
    )

    # --- tenant_modules -----------------------------------------------------
    op.create_table(
        "tenant_modules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "module_id", name="uq_tenant_module"),
    )
    op.create_index("ix_tenant_modules_tenant", "tenant_modules", ["tenant_id"])
    op.create_index("ix_tenant_modules_module", "tenant_modules", ["module_id"])

    # --- compliance_results -------------------------------------------------
    op.create_table(
        "compliance_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_compliance_results_tenant", "compliance_results", ["tenant_id"])
    op.create_index("ix_compliance_results_recorded", "compliance_results", ["recorded_at"])
    op.create_index("ix_compliance_results_module", "compliance_results", ["module"])

    # --- file_visibility_results -------------------------------------------
    op.create_table(
        "file_visibility_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("share_name", sa.String(length=255), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_file_visibility_agent", "file_visibility_results", ["agent_id"])
    op.create_index("ix_file_visibility_recorded", "file_visibility_results", ["recorded_at"])

    # --- network_visibility_results ----------------------------------------
    op.create_table(
        "network_visibility_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("service", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_network_visibility_agent", "network_visibility_results", ["agent_id"])
    op.create_index("ix_network_visibility_recorded", "network_visibility_results", ["recorded_at"])


def downgrade() -> None:
    op.drop_index("ix_network_visibility_recorded", table_name="network_visibility_results")
    op.drop_index("ix_network_visibility_agent", table_name="network_visibility_results")
    op.drop_table("network_visibility_results")

    op.drop_index("ix_file_visibility_recorded", table_name="file_visibility_results")
    op.drop_index("ix_file_visibility_agent", table_name="file_visibility_results")
    op.drop_table("file_visibility_results")

    op.drop_index("ix_compliance_results_module", table_name="compliance_results")
    op.drop_index("ix_compliance_results_recorded", table_name="compliance_results")
    op.drop_index("ix_compliance_results_tenant", table_name="compliance_results")
    op.drop_table("compliance_results")

    op.drop_index("ix_tenant_modules_module", table_name="tenant_modules")
    op.drop_index("ix_tenant_modules_tenant", table_name="tenant_modules")
    op.drop_table("tenant_modules")

    op.drop_table("modules")

    op.drop_index("ix_agents_token", table_name="agents")
    op.drop_column("agents", "token")
