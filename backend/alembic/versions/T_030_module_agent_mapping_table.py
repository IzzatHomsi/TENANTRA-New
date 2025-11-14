"""Ensure module_agent_mapping table exists for agent overrides."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "T_030_module_agent_mapping_table"
down_revision = "T_029_merge_schema_heads"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "module_agent_mapping" in inspector.get_table_names():
        return
    op.create_table(
        "module_agent_mapping",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("module_id", "agent_id", name="_module_agent_uc"),
    )
    op.create_index("ix_module_agent_mapping_module_id", "module_agent_mapping", ["module_id"])
    op.create_index("ix_module_agent_mapping_agent_id", "module_agent_mapping", ["agent_id"])


def downgrade():
    op.drop_index("ix_module_agent_mapping_agent_id", table_name="module_agent_mapping")
    op.drop_index("ix_module_agent_mapping_module_id", table_name="module_agent_mapping")
    op.drop_table("module_agent_mapping")
