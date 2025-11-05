"""Fix heads

Revision ID: d425e646fc13
Revises: 0006_add_timestamps_log, 0007_add_ip_to_audit_log
Create Date: 2025-08-07
"""

from alembic import op
import sqlalchemy as sa

revision = 'd425e646fc13'
down_revision = ('0006_add_timestamps_log', '0007_add_ip_to_audit_log')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass