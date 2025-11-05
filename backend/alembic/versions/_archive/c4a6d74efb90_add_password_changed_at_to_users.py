"""Add password_changed_at to users"""

revision = 'c4a6d74efb90'
down_revision = 'd425e646fc13'  # <-- should match the last migration
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(), nullable=True))
    # (plus other columns like expires_at, last_login_at, etc)

def downgrade():
    op.drop_column('users', 'password_changed_at')
    # (and remove other fields if they exist)
