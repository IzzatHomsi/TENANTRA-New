"""Add user login/expiry tracking fields"""

from alembic import op
import sqlalchemy as sa

# Unique migration identifiers
revision = 'b5eda931c8e4'
down_revision = 'c4a6d74efb90'  # Replace with the last correct migration hash
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('expires_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_action_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('users', 'expires_at')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'last_action_at')
