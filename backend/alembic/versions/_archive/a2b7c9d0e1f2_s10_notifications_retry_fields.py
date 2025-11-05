"""
S-10: Notifications retry fields (attempts, next_attempt_at, last_error)

Adds columns if missing:
- attempts INTEGER NOT NULL DEFAULT 0
- next_attempt_at TIMESTAMP NULL
- last_error TEXT NULL
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a2b7c9d0e1f2"
down_revision = "7f9a2c1e6b01"
branch_labels = None
depends_on = None


def _has_column(conn, table, column):
    q = sa.text("SELECT 1 FROM information_schema.columns WHERE table_name=:t AND column_name=:c")
    return bool(conn.execute(q, dict(t=table, c=column)).scalar())


def upgrade():
    conn = op.get_bind()

    if not _has_column(conn, "notifications", "attempts"):
        op.add_column("notifications", sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"))
        op.alter_column("notifications", "attempts", server_default=None)

    if not _has_column(conn, "notifications", "next_attempt_at"):
        op.add_column("notifications", sa.Column("next_attempt_at", sa.DateTime(), nullable=True))

    if not _has_column(conn, "notifications", "last_error"):
        op.add_column("notifications", sa.Column("last_error", sa.Text(), nullable=True))


def downgrade():
    conn = op.get_bind()

    # Drop columns if present
    for col in ["last_error", "next_attempt_at", "attempts"]:
        q = sa.text("SELECT 1 FROM information_schema.columns WHERE table_name='notifications' AND column_name=:c")
        if conn.execute(q, dict(c=col)).scalar():
            op.drop_column("notifications", col)
