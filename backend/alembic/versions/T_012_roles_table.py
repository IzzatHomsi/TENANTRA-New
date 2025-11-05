"""Create roles table to back Role model and /roles endpoint.

Revision ID: T_012_roles_table
Revises: T_011_module_metadata_columns
Create Date: 2025-10-19
"""

from alembic import op
import sqlalchemy as sa


revision = "T_012_roles_table"
down_revision = "T_011_module_metadata_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")

