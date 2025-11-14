"""Add missing audit log columns for action/result/ip tracking."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "T_028_audit_log_enrichment"
down_revision = "T_027_unify_scan_jobs"
branch_labels = None
depends_on = None


def _inspector():
    bind = op.get_bind()
    return sa.inspect(bind)


def upgrade():
    inspector = _inspector()
    columns = {col["name"] for col in inspector.get_columns("audit_logs")}
    with op.batch_alter_table("audit_logs", schema=None) as batch_op:
        if "action" not in columns:
            batch_op.add_column(sa.Column("action", sa.String(length=100), nullable=True))
        if "result" not in columns:
            batch_op.add_column(sa.Column("result", sa.String(length=50), nullable=True))
        if "ip" not in columns:
            batch_op.add_column(sa.Column("ip", sa.String(length=45), nullable=True))

    indexes = {idx["name"] for idx in inspector.get_indexes("audit_logs")}
    if "ix_audit_logs_result" not in indexes:
        op.create_index("ix_audit_logs_result", "audit_logs", ["result"])


def downgrade():
    inspector = _inspector()
    indexes = {idx["name"] for idx in inspector.get_indexes("audit_logs")}
    if "ix_audit_logs_result" in indexes:
        op.drop_index("ix_audit_logs_result", table_name="audit_logs")

    columns = {col["name"] for col in inspector.get_columns("audit_logs")}
    with op.batch_alter_table("audit_logs", schema=None) as batch_op:
        if "ip" in columns:
            batch_op.drop_column("ip")
        if "result" in columns:
            batch_op.drop_column("result")
        if "action" in columns:
            batch_op.drop_column("action")
