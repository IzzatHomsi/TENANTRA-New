"""Phase 2 schema health fixes."""

from __future__ import annotations

from typing import List

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "T_025_phase2_schema_health"
down_revision = "T_024_agent_enrollment_tokens"
branch_labels = None
depends_on = None


def _get_inspector():
    bind = op.get_bind()
    return sa.inspect(bind)


def _ensure_timestamp_columns() -> None:
    inspector = _get_inspector()
    for table in inspector.get_table_names():
        if table in {"alembic_version", "notification_settings"}:
            continue
        columns = {col["name"] for col in inspector.get_columns(table)}
        needs_created = "created_at" not in columns
        needs_updated = "updated_at" not in columns
        if not needs_created and not needs_updated:
            continue
        with op.batch_alter_table(table, schema=None) as batch:
            if needs_created:
                batch.add_column(
                    sa.Column(
                        "created_at",
                        sa.DateTime(),
                        nullable=False,
                        server_default=sa.text("timezone('utc', now())"),
                    )
                )
            if needs_updated:
                batch.add_column(
                    sa.Column(
                        "updated_at",
                        sa.DateTime(),
                        nullable=False,
                        server_default=sa.text("timezone('utc', now())"),
                    )
                )


def _standardize_json_columns() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    jsonb = postgresql.JSONB(astext_type=sa.Text())
    op.alter_column(
        "modules",
        "parameter_schema",
        type_=jsonb,
        postgresql_using="parameter_schema::jsonb",
    )
    op.alter_column(
        "process_drift_events",
        "old_value",
        type_=jsonb,
        postgresql_using="old_value::jsonb",
    )
    op.alter_column(
        "process_drift_events",
        "new_value",
        type_=jsonb,
        postgresql_using="new_value::jsonb",
    )


def _simplify_module_status() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("modules")}
    if "enabled" in columns:
        op.execute(
            "UPDATE modules SET status = LOWER(status) WHERE status IS NOT NULL"
        )
        op.execute(
            "UPDATE modules SET status = 'active' WHERE status IS NULL OR status = ''"
        )
        op.execute(
            """
            UPDATE modules
            SET status = 'disabled'
            WHERE COALESCE(enabled, false) = false
              AND status NOT IN ('disabled','deprecated','retired')
            """
        )
        status_enum = sa.Enum(
            "draft",
            "active",
            "disabled",
            "deprecated",
            "retired",
            name="module_status",
        )
        status_enum.create(bind, checkfirst=True)
        with op.batch_alter_table("modules", schema=None) as batch:
            batch.alter_column(
                "status",
                existing_type=sa.String(length=50),
                type_=status_enum,
                nullable=False,
                server_default="active",
            )
            batch.drop_column("enabled")


def _drop_notification_settings() -> None:
    inspector = _get_inspector()
    if "notification_settings" in inspector.get_table_names():
        op.drop_table("notification_settings")


def _ensure_fk_indexes() -> None:
    inspector = _get_inspector()
    for table in inspector.get_table_names():
        if table == "alembic_version":
            continue
        existing = {
            tuple(idx["column_names"])
            for idx in inspector.get_indexes(table)
            if idx.get("column_names")
        }
        for fk in inspector.get_foreign_keys(table):
            cols = tuple(fk.get("constrained_columns") or [])
            if not cols:
                continue
            if cols in existing:
                continue
            index_name = f"ix_{table}_{'_'.join(cols)}"
            op.create_index(index_name, table, list(cols))
            existing.add(cols)


def _recreate_fk(
    table: str, column: str, referred_table: str, ondelete: str
) -> None:
    inspector = _get_inspector()
    fk_name = None
    for fk in inspector.get_foreign_keys(table):
        cols = fk.get("constrained_columns") or []
        if len(cols) == 1 and cols[0] == column and fk.get("referred_table") == referred_table:
            fk_name = fk.get("name")
            break
    if fk_name:
        op.drop_constraint(fk_name, table_name=table, type_="foreignkey")
    op.create_foreign_key(
        f"fk_{table}_{column}",
        source_table=table,
        referent_table=referred_table,
        local_cols=[column],
        remote_cols=["id"],
        ondelete=ondelete,
    )


def upgrade() -> None:
    _ensure_timestamp_columns()
    _standardize_json_columns()
    _simplify_module_status()
    _drop_notification_settings()
    _ensure_fk_indexes()
    _recreate_fk("users", "tenant_id", "tenants", "CASCADE")
    _recreate_fk("agents", "tenant_id", "tenants", "CASCADE")
    _recreate_fk("assets", "tenant_id", "tenants", "CASCADE")
    _recreate_fk("module_agent_mapping", "module_id", "modules", "CASCADE")
    _recreate_fk("module_agent_mapping", "agent_id", "agents", "CASCADE")


def downgrade() -> None:
    raise RuntimeError("Phase 2 migration is not reversible.")
