"""Merge all stray heads into a single canonical head.

Revision ID: af01c2d3e4f6
Revises: 0007_add_ip_to_audit_log, 0008, 65eed4fc5c8a, e3b32b8c1b9c, e9f1a2b3c4d5, m20250814184912
Create Date: 2025-09-03T13:29:59

This is a no-op merge revision to consolidate multiple concurrent heads
into a single linear history. It does not modify schema.
"""

from alembic import op  # noqa
import sqlalchemy as sa  # noqa

# revision identifiers, used by Alembic.
revision = "af01c2d3e4f6"
down_revision = ['0007_add_ip_to_audit_log', '0008', '65eed4fc5c8a', 'e3b32b8c1b9c', 'e9f1a2b3c4d5', 'm20250814184912']
branch_labels = None
depends_on = None


def upgrade():
    # No-op merge
    pass


def downgrade():
    # No-op merge
    pass
