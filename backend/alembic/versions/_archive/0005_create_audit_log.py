"""create_audit_log_table

Revision ID: 0005_create_audit_log
Revises: 0004_create_roles
Create Date: 2025-08-07
"""

from alembic import op
import sqlalchemy as sa

revision = '0005_create_audit_log'
down_revision = '0004_create_roles'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('ip', sa.String(), nullable=True),
        sa.Column('result', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )

def downgrade():
    op.drop_table('audit_logs')