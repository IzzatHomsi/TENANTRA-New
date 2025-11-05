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
from alembic import op                         # Alembic operations helper
import sqlalchemy as sa                        # SQLAlchemy for types/introspection


# --- Alembic identifiers ---
revision = "T_001_add_tenants_and_fk"
down_revision = "T_000_unified_base"
branch_labels = None
depends_on = None


# ---------------------------
# Introspection helper funcs
# ---------------------------
def _insp(conn):
    """Return a SQLAlchemy Inspector bound to the current connection."""
    return sa.inspect(conn)

def _has_table(conn, name: str) -> bool:
    """True if a table exists in the current schema."""
    return _insp(conn).has_table(name)

def _has_column(conn, table: str, col: str) -> bool:
    """True if a table has a given column (and the table itself exists)."""
    insp = _insp(conn)
    if not insp.has_table(table):
        return False
    return col in [c["name"] for c in insp.get_columns(table)]

def _has_fk(conn, table: str, fk_name: str) -> bool:
    """True if a FK with a specific name already exists on a table."""
    insp = _insp(conn)
    if not insp.has_table(table):
        return False
    return any(f.get("name") == fk_name for f in insp.get_foreign_keys(table) if f.get("name"))

def _has_index(conn, table: str, idx_name: str) -> bool:
    """True if an index with the given name exists on a table."""
    insp = _insp(conn)
    if not insp.has_table(table):
        return False
    return any(ix.get("name") == idx_name for ix in insp.get_indexes(table))


def upgrade():
    """Apply schema changes & backfill in a way that tolerates legacy shapes."""
    conn = op.get_bind()

    # ----------------------------------------------
    # 1) Ensure TENANTS table exists with all columns
    # ----------------------------------------------
    if not _has_table(conn, "tenants"):
        # Fresh create with the full, expected shape.
        op.create_table(
            "tenants",
            sa.Column("id", sa.Integer, primary_key=True),                             # PK
            sa.Column("name", sa.String(length=255), nullable=False, unique=True),     # human name
            sa.Column("slug", sa.String(length=255), nullable=True, unique=True),      # URL/key-friendly
            sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
            sa.Column("storage_quota_gb", sa.Integer, nullable=True, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    else:
        # Legacy table exists — add any missing columns safely.
        if not _has_column(conn, "tenants", "name"):
            op.add_column("tenants", sa.Column("name", sa.String(length=255), nullable=False))
        if not _has_column(conn, "tenants", "slug"):
            # nullable=True so we don't violate not-null on legacy rows
            op.add_column("tenants", sa.Column("slug", sa.String(length=255), nullable=True))
        if not _has_column(conn, "tenants", "is_active"):
            op.add_column("tenants", sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")))
        if not _has_column(conn, "tenants", "storage_quota_gb"):
            op.add_column("tenants", sa.Column("storage_quota_gb", sa.Integer, nullable=True, server_default=sa.text("0")))
        if not _has_column(conn, "tenants", "created_at"):
            op.add_column("tenants", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        if not _has_column(conn, "tenants", "updated_at"):
            op.add_column("tenants", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

    # Helpful indexes (non-unique to avoid conflicts where a unique constraint already exists).
    if not _has_index(conn, "tenants", "ix_tenants_name"):
        op.create_index("ix_tenants_name", "tenants", ["name"], unique=False)
    if not _has_index(conn, "tenants", "ix_tenants_slug"):
        op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=False)

    # ----------------------------------------------------------
    # 2) Ensure USERS.tenant_id column & create FK (guarded)
    # ----------------------------------------------------------
    if _has_table(conn, "users") and not _has_column(conn, "users", "tenant_id"):
        op.add_column("users", sa.Column("tenant_id", sa.Integer, nullable=True))  # keep nullable for backfill first

    fk_name = "fk_users_tenant_id_tenants"
    if not _has_fk(conn, "users", fk_name):
        # We will create the FK after we are sure a default tenant exists and users are normalized.
        pass  # created later after backfill

    # ----------------------------------------------------------
    # 3) Ensure default tenant exists (id=1) — tolerant & safe
    # ----------------------------------------------------------
    # At this point, tenants table has the necessary columns (including 'slug').
    op.execute(
        """
        INSERT INTO tenants (id, name, slug, is_active, storage_quota_gb)
        VALUES (1, 'Default Tenant', 'default-tenant', TRUE, 0)
        ON CONFLICT (id) DO NOTHING
        """
    )

    # If 'tenants.id' uses a sequence/identity, bump it to at least MAX(id).
    # Use a plpgsql DO block to silently ignore missing sequences in edge cases.
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
            -- ignore if no sequence is attached (identity or manual ids)
            NULL;
        END $$;
        """
    )

    # ----------------------------------------------------------
    # 4) Normalize existing USERS.tenant_id -> 1 where NULL/invalid
    # ----------------------------------------------------------
    if _has_table(conn, "users") and _has_column(conn, "users", "tenant_id"):
        op.execute(
            """
            UPDATE users
               SET tenant_id = 1
             WHERE tenant_id IS NULL
                OR tenant_id NOT IN (SELECT id FROM tenants)
            """
        )

    # ----------------------------------------------------------
    # 5) Create FK now that backfill is safe
    # ----------------------------------------------------------
    if not _has_fk(conn, "users", fk_name) and _has_table(conn, "users") and _has_column(conn, "users", "tenant_id"):
        op.create_foreign_key(
            fk_name,
            source_table="users",
            referent_table="tenants",
            local_cols=["tenant_id"],
            remote_cols=["id"],
            ondelete="CASCADE",
        )


def downgrade():
    """Reverse changes (best-effort; keep safe in presence of partial legacy states)."""
    # Drop FK if present
    try:
        op.drop_constraint("fk_users_tenant_id_tenants", "users", type_="foreignkey")
    except Exception:
        pass

    # Drop indexes (safe if present)
    try:
        op.drop_index("ix_tenants_slug", table_name="tenants")
    except Exception:
        pass
    try:
        op.drop_index("ix_tenants_name", table_name="tenants")
    except Exception:
        pass

    # Finally drop the table (if it exists)
    try:
        op.drop_table("tenants")
    except Exception:
        pass
