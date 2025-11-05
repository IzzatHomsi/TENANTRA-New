"""Unified canonical base schema (single-head) — v2 (adds users.tenant_id, users.role).

This migration intentionally collapses all previous branches into a single, canonical head.
It is safe to apply on a fresh database and is meant to be the only head on DEV.
"""

from alembic import op  # Alembic operations helper (create_table, add_column, etc.)
import sqlalchemy as sa  # SQLAlchemy types and expressions

# Revision identifiers, used by Alembic.
revision = "T_000_unified_base"  # Human-friendly id so you can spot it quickly with `alembic heads`
down_revision = None             # No parent: this is the root of the tree (single head)
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- tenants ---------------------------------------------------------
    # Small, stable anchor table for multi-tenant scoping.
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),  # PK: simple, fast integer
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),  # Unique human name
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_tenants_name", "tenants", ["name"], unique=False)

    # --- users -----------------------------------------------------------
    # Core identity table used by auth, RBAC, and ownership.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=150), nullable=False),                # login handle
        sa.Column("password_hash", sa.String(length=255), nullable=False),           # bcrypt/argon2 hash
        sa.Column("email", sa.String(length=255), nullable=True),                    # optional, can be null for service users
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        # v2 additions kept in base for fresh installs:
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True),
        sa.Column("role", sa.String(length=50), server_default=sa.text("'admin'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=False)


def downgrade() -> None:
    # Order matters due to FKs.
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_tenants_name", table_name="tenants")
    op.drop_table("tenants")
