"""Add notification_settings table to support user management flows.

Revision ID: T_005_notification_settings
Revises: T_004_alerts_refresh_tokens
Create Date: 2025-09-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "T_005_notification_settings"
down_revision = "T_004_alerts_refresh_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_notification_settings_recipient", "notification_settings", ["recipient_id"])
    op.create_index("ix_notification_settings_tenant", "notification_settings", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_notification_settings_tenant", table_name="notification_settings")
    op.drop_index("ix_notification_settings_recipient", table_name="notification_settings")
    op.drop_table("notification_settings")
