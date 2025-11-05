"""create_roles_table

Revision ID: 0004_create_roles
Revises: 0003_add_role_column_to_users
Create Date: 2025-07-30

"""
from alembic import op
import sqlalchemy as sa

revision = '0004_create_roles'
down_revision = '0003_add_role_column_to_users'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True)
    )

def downgrade():
    op.drop_table('roles')