"""Ensure audit_logs has indexes for common filters."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "4c8d7a9b2d4f"
down_revision = "3d2b8f8a7e3c"
branch_labels = None
depends_on = None

# (name, columns)
INDEX_DEFS = (
    ("ix_audit_logs_user_id", ["user_id"]),
    ("ix_audit_logs_result", ["result"]),
    ("ix_audit_logs_created_at", ["created_at"]),
)


def _inspector():
    bind = op.get_bind()
    return sa.inspect(bind)


def upgrade() -> None:
    inspector = _inspector()
    existing = {idx["name"] for idx in inspector.get_indexes("audit_logs")}
    existing_cols = {col["name"] for col in inspector.get_columns("audit_logs")}
    for name, columns in INDEX_DEFS:
        if name in existing:
            continue
        if any(col not in existing_cols for col in columns):
            # Older/deviated schemas may lack optional columns; skip instead of failing.
            continue
        op.create_index(name, "audit_logs", columns)


def downgrade() -> None:
    inspector = _inspector()
    existing = {idx["name"] for idx in inspector.get_indexes("audit_logs")}
    for name, _ in INDEX_DEFS:
        if name in existing:
            op.drop_index(name, table_name="audit_logs")
