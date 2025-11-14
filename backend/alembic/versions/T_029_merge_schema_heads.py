"""Merge audit index branch into main schema chain."""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "T_029_merge_schema_heads"
down_revision = ("T_028_audit_log_enrichment", "4c8d7a9b2d4f")
branch_labels = None
depends_on = None


def upgrade():
    # No-op merge revision to unify Alembic heads.
    pass


def downgrade():
    # Splitting heads again is not supported.
    raise RuntimeError("Downgrading merge revision T_029_merge_schema_heads is not supported")
