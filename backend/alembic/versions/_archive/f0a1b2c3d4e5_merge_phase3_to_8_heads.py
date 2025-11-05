"""Canonical merge for Phase 3–8 heads.

- Replaces ad-hoc merge scripts:
  * 0008_merge_multiple_heads.py
  * d425e646fc13_fix_heads.py
- Ensures a single linear head for subsequent revisions.

"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# Revision identifiers, used by Alembic.
revision = "f0a1b2c3d4e5"
# NOTE: These are the two known heads observed in your repo. If `alembic heads`
# shows more, add them to this tuple before applying.
down_revision = ("b5eda931c8e4", "e3b32b8c1b9c")
branch_labels = None
depends_on = None


def upgrade():
    # Pure merge revision: no schema ops.
    pass


def downgrade():
    # Non-trivial to downgrade a merge; keep as no-op to preserve history integrity.
    pass
