"""Add IP column to audit_logs if not already exists"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '0007_add_ip_to_audit_log'
down_revision = '0006_add_timestamps_log'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("audit_logs")]
    if "ip" not in columns:
        op.add_column("audit_logs", sa.Column("ip", sa.String(), nullable=True))

def downgrade():
    op.drop_column("audit_logs", "ip")
