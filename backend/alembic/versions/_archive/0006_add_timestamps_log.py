"""add timestamps to roles and audit_logs tables

Revision ID: 0006_add_timestamps
Revises: 0005_create_audit_logs
Create Date: 2025-08-06

This migration adds created_at and updated_at columns to the roles and
audit_logs tables. These timestamp columns align the database schema
with the SQLAlchemy models that use the TimestampMixin. If your
database already contains these tables, running this migration will
add the missing columns without altering existing data.
"""

from alembic import op
import sqlalchemy as sa

revision = '0006_add_timestamps_log'
down_revision = '0005_create_audit_logs'
# The previous revision ID that this migration depends on. We insert a dummy
# migration ('c9b6e26a1dee') ahead of this one to satisfy Alembic's
# revision chain when older databases reference a non‑existent revision.
down_revision = 'c9b6e26a1dee'
branch_labels = None
depends_on = None


def upgrade():

    conn = op.get_bind()
    # Roles table
    op.execute("""ALTER TABLE IF EXISTS roles
                 ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE""")
    op.execute("""ALTER TABLE IF EXISTS roles
                 ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE""")
    # Audit log table
    op.execute("""ALTER TABLE IF EXISTS audit_log
                 ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE""")
    op.execute("""ALTER TABLE IF EXISTS audit_log
                 ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE""")

def downgrade():
    # Remove the timestamp columns from audit_logs and roles tables if
    # this migration is rolled back.
    op.drop_column('audit_logs', 'updated_at')
    op.drop_column('audit_logs', 'created_at')
    op.drop_column('roles', 'updated_at')
    op.drop_column('roles', 'created_at')