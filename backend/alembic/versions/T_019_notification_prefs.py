"""notification preferences table

Revision ID: T_019_notification_prefs
Revises: T_018_scheduled_scans_parameters
Create Date: 2025-10-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'T_019_notification_prefs'
down_revision = 'T_018_scheduled_scans_parameters'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notification_prefs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('channels', sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('events', sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('digest', sa.String(length=32), nullable=False, server_default='immediate'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_notification_prefs_tenant_user', 'notification_prefs', ['tenant_id', 'user_id'])


def downgrade() -> None:
    op.drop_index('ix_notification_prefs_tenant_user', table_name='notification_prefs')
    op.drop_table('notification_prefs')

