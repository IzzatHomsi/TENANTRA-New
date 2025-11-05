"""Canonical merge of active heads.

This revision merges 9193c31a0b5b and m20250814184912 into a single lineage.
No schema ops; merge only.
"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision = "65eed4fc5c8a"
down_revision = ('9193c31a0b5b', 'm20250814184912')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op merge; schema already represented by parent heads.
    pass


def downgrade() -> None:
    # No-op.
    pass