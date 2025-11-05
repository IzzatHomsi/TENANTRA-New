"""Add tenants table and FK to users (follow-on fix, hardened & backfill).

Revision ID: T_001_add_tenants_and_fk
Revises: T_000_unified_base
Create Date: 2025-09-15

What this migration guarantees (idempotently and safely):
1) A 'tenants' table exists with expected columns: id, name, slug, is_active,
   storage_quota_gb, created_at, updated_at. If the table already exists but
   some columns are missing (legacy shape), the missing columns are added.
2) A default tenant (id=1, name='Default Tenant', slug='default-tenant') exists.
3) 'users.tenant_id' column exists and is bound by a FK to tenants(id).
4) Existing users get a valid 'tenant_id' (1) if NULL or invalid.

This keeps a single, linear head: T_000_unified_base -> T_001_add_tenants_and_fk.
"""
from alembic import op
import sqlalchemy as sa


# --- Alembic identifiers ---
revision = "T_001_add_tenants_and_fk"
down_revision = "T_000_unified_base"
branch_labels = None
depends_on = None


# ---------------------------
# Introspection helper funcs
# ---------------------------
def _insp(conn):
    return sa.inspect(conn)

def _has_table(conn, name: str) -> bool:
    return _insp(conn).has_table(name)

def _has_column(conn, table: str, col: str) -> bool:
    insp = _insp(conn)
    if not insp.has_table(table):
        return False
    return col in [c["name"] for c in insp.get_columns(table)]

def _has_index(conn, table: str, idx_name: str) -> bool:
    insp = _insp(conn)
    if not insp.has_table(table):
        return False
    return any(ix.get("name") == idx_name for ix in insp.get_indexes(table))

def _has_users_tenant_fk(conn) -> bool:
    """Return True if ANY FK exists from users(tenant_id) -> tenants(id),
    regardless of the constraint name (covers autonamed FKs from earlier migrations)."""
    insp = _insp(conn)
    if not insp.has_table("users"):
        return False
    for fk in insp.get_foreign_keys("users"):
        cols = fk.get("constrained_columns") or []
        referred_table = fk.get("referred_table")
        referred_cols = fk.get("referred_columns") or []
        if len(cols) == 1 and cols[0] == "tenant_id" and referred_table == "tenants" and referred_cols == ["id"]:
            return True
    return False


def upgrade():
    conn = op.get_bind()

    # 1) Ensure TENANTS table exists with all columns
    if not _has_table(conn, "tenants"):
        op.create_table(
            "tenants",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False, unique=True),
            sa.Column("slug", sa.String(length=255), nullable=True, unique=True),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
            sa.Column("storage_quota_gb", sa.Integer, nullable=True, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    else:
        if not _has_column(conn, "tenants", "name"):
            op.add_column("tenants", sa.Column("name", sa.String(length=255), nullable=False))
        if not _has_column(conn, "tenants", "slug"):
            op.add_column("tenants", sa.Column("slug", sa.String(length=255), nullable=True))
        if not _has_column(conn, "tenants", "is_active"):
            op.add_column("tenants", sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")))
        if not _has_column(conn, "tenants", "storage_quota_gb"):
            op.add_column("tenants", sa.Column("storage_quota_gb", sa.Integer, nullable=True, server_default=sa.text("0")))
        if not _has_column(conn, "tenants", "created_at"):
            op.add_column("tenants", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        if not _has_column(conn, "tenants", "updated_at"):
            op.add_column("tenants", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

    # Helpful indexes (guarded)
    if not _has_index(conn, "tenants", "ix_tenants_name"):
        op.create_index("ix_tenants_name", "tenants", ["name"], unique=False)
    if not _has_index(conn, "tenants", "ix_tenants_slug"):
        op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=False)

    # 2) Ensure USERS.tenant_id column exists
    if _has_table(conn, "users") and not _has_column(conn, "users", "tenant_id"):
        op.add_column("users", sa.Column("tenant_id", sa.Integer, nullable=True))  # nullable until backfill

    # 3) Ensure default tenant
    op.execute(
        """
        INSERT INTO tenants (id, name, slug, is_active, storage_quota_gb)
        VALUES (1, 'Default Tenant', 'default-tenant', TRUE, 0)
        ON CONFLICT (id) DO NOTHING
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            PERFORM setval(
                pg_get_serial_sequence('tenants','id'),
                GREATEST(1, (SELECT COALESCE(MAX(id),1) FROM tenants)),
                true
            );
        EXCEPTION WHEN others THEN
            NULL;
        END $$;
        """
    )

    # 4) Backfill USERS.tenant_id
    if _has_table(conn, "users") and _has_column(conn, "users", "tenant_id"):
        op.execute(
            """
            UPDATE users
               SET tenant_id = 1
             WHERE tenant_id IS NULL
                OR tenant_id NOT IN (SELECT id FROM tenants)
            """
        )

    # 5) Create FK if it doesn't already exist (by relationship, not name)
    if _has_table(conn, "users") and _has_column(conn, "users", "tenant_id") and not _has_users_tenant_fk(conn):
        op.create_foreign_key(
            "fk_users_tenant_id_tenants",
            source_table="users",
            referent_table="tenants",
            local_cols=["tenant_id"],
            remote_cols=["id"],
            ondelete="CASCADE",
        )


def downgrade():
    try:
        op.drop_constraint("fk_users_tenant_id_tenants", "users", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_index("ix_tenants_slug", table_name="tenants")
    except Exception:
        pass
    try:
        op.drop_index("ix_tenants_name", table_name="tenants")
    except Exception:
        pass
    try:
        op.drop_table("tenants")
    except Exception:
        pass
