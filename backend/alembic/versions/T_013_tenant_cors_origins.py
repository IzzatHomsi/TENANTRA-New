"""Create tenant_cors_origins table for per-tenant CORS allowlist.

Revision ID: T_013_tenant_cors_origins
Revises: T_012_roles_table
Create Date: 2025-10-20
"""

from alembic import op
import sqlalchemy as sa


revision = "T_013_tenant_cors_origins"
down_revision = "T_012_roles_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_cors_origins",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("is_global", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("tenant_id", "origin", name="uq_tenant_origin"),
    )
    op.create_index("ix_tenant_cors_origin", "tenant_cors_origins", ["origin"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tenant_cors_origin", table_name="tenant_cors_origins")
    op.drop_table("tenant_cors_origins")

