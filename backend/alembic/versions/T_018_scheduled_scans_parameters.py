"""Add JSONB parameters to scheduled_scans

Revision ID: T_018_scheduled_scans_parameters
Revises: T_017_registry_task_baselines
Create Date: 2025-10-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "T_018_scheduled_scans_parameters"
down_revision = "T_017_registry_task_baselines"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scheduled_scans",
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("scheduled_scans", "parameters")

