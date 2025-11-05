from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '0002_add_email_is_active'
down_revision = '0001_initial'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true'))

def downgrade():
    op.drop_column('users', 'email')
    op.drop_column('users', 'is_active')