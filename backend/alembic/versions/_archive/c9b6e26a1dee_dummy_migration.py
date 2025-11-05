"""dummy migration to bridge missing revision"""

from alembic import op
import sqlalchemy as sa

revision = 'c9b6e26a1dee'
down_revision = '0005_create_audit_log'
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass