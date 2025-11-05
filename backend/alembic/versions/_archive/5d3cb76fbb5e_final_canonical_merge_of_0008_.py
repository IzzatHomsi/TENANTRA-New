"""Final canonical merge of 0008 and f0a1b2c3d4e5."""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# Revision identifiers, used by Alembic.
revision = "5d3cb76fbb5e"
down_revision = ("0008", "f0a1b2c3d4e5")
branch_labels = None
depends_on = None


def upgrade():
    # Pure merge revision: no schema operations.
    pass


def downgrade():
    # Non-destructive no-op for the merge point.
    pass
