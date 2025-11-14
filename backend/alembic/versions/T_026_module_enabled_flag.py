"""Add module.enabled flag with default false."""

from alembic import op
import sqlalchemy as sa


revision = "T_026_module_enabled_flag"
down_revision = "T_025_phase2_schema_health"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "modules",
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute("UPDATE modules SET enabled = TRUE")


def downgrade():
    op.drop_column("modules", "enabled")
