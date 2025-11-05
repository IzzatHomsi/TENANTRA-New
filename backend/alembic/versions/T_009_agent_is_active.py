
"""Add is_active flag to agents"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "T_009_agent_is_active"
down_revision = "T_008_scheduled_scans"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agents", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.execute("UPDATE agents SET is_active = TRUE WHERE is_active IS NULL")
    op.alter_column("agents", "is_active", nullable=False, server_default=sa.true())


def downgrade() -> None:
    op.drop_column("agents", "is_active")
