"""Initial migration

Revision ID: 0001_initial
Revises:
Create Date: 2025-07-23
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, nullable=False, unique=True),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id')),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )

def downgrade():
    op.drop_table('users')
    op.drop_table('tenants')