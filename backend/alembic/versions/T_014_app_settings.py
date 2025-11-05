"""Create app_settings table for global/tenant configuration.

Revision ID: T_014_app_settings
Revises: T_013_tenant_cors_origins
Create Date: 2025-10-20
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "T_014_app_settings"
down_revision = "T_013_tenant_cors_origins"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("tenant_id", "key", name="uq_app_settings_scope_key"),
    )
    op.create_index("ix_app_settings_tenant_key", "app_settings", ["tenant_id", "key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_app_settings_tenant_key", table_name="app_settings")
    op.drop_table("app_settings")

