"""Canonical merge of multiple heads generated on 20250901104534.

This revision merges the following heads into a single lineage:
['c9b6e26a1dee', 'e9f1a2b3c4d5', 'e3b32b8c1b9c', 'f0a1b2c3d4e5', '0008']
"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision = "9193c31a0b5b"
down_revision = ('c9b6e26a1dee', 'e9f1a2b3c4d5', 'e3b32b8c1b9c', 'f0a1b2c3d4e5', '0008')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op merge; schema already represented by parent heads.
    pass


def downgrade() -> None:
    # Non-trivial to downgrade a merge; leaving as no-op.
    pass
