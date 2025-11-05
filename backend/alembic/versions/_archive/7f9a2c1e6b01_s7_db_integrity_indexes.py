"""
S-7: DB Integrity — indexes & unique constraints (safe & idempotent)

- Ensures unique constraints on:
  * roles.name
  * modules.name
  * users.username
  * users.email
- Ensures commonly used indexes:
  * users(tenant_id), users(role)
  * audit_logs(user_id), audit_logs(timestamp)
  * assets(tenant_id), assets(hostname), assets(ip_address)
- No destructive changes; operations are guarded by inspector checks.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "7f9a2c1e6b01"
down_revision = "5d3cb76fbb5e"
branch_labels = None
depends_on = None


def _constraint_exists(conn, table, name):
    q = sa.text("""
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name=:table AND constraint_name=:name
    """)
    return bool(conn.execute(q, dict(table=table, name=name)).scalar())


def _index_exists(conn, index_name):
    q = sa.text("""
        SELECT 1 FROM pg_indexes WHERE indexname = :idx
    """)
    return bool(conn.execute(q, dict(idx=index_name)).scalar())


def upgrade():
    conn = op.get_bind()

    # --- roles.name unique ---
    if not _constraint_exists(conn, 'roles', 'uq_roles_name'):
        op.create_unique_constraint('uq_roles_name', 'roles', ['name'])

    # --- modules.name unique ---
    if not _constraint_exists(conn, 'modules', 'uq_module_name'):
        op.create_unique_constraint('uq_module_name', 'modules', ['name'])

    # --- users.username unique ---
    if not _constraint_exists(conn, 'users', 'uq_users_username'):
        op.create_unique_constraint('uq_users_username', 'users', ['username'])

    # --- users.email unique ---
    if not _constraint_exists(conn, 'users', 'uq_users_email'):
        op.create_unique_constraint('uq_users_email', 'users', ['email'])

    # --- users tenant_id index ---
    if not _index_exists(conn, 'ix_users_tenant_id'):
        op.create_index('ix_users_tenant_id', 'users', ['tenant_id'], unique=False)

    # --- users role index ---
    if not _index_exists(conn, 'ix_users_role'):
        op.create_index('ix_users_role', 'users', ['role'], unique=False)

    # --- audit_logs user_id index ---
    if not _index_exists(conn, 'ix_audit_logs_user_id'):
        op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)

    # --- audit_logs timestamp index ---
    if not _index_exists(conn, 'ix_audit_logs_timestamp'):
        op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], unique=False)

    # --- assets tenant_id index ---
    if not _index_exists(conn, 'ix_assets_tenant_id'):
        op.create_index('ix_assets_tenant_id', 'assets', ['tenant_id'], unique=False)

    # --- assets hostname index ---
    if not _index_exists(conn, 'ix_assets_hostname'):
        op.create_index('ix_assets_hostname', 'assets', ['hostname'], unique=False)

    # --- assets ip_address index ---
    if not _index_exists(conn, 'ix_assets_ip_address'):
        op.create_index('ix_assets_ip_address', 'assets', ['ip_address'], unique=False)


def downgrade():
    conn = op.get_bind()

    # Drop indexes if they exist (safe order)
    for idx in [
        'ix_assets_ip_address',
        'ix_assets_hostname',
        'ix_assets_tenant_id',
        'ix_audit_logs_timestamp',
        'ix_audit_logs_user_id',
        'ix_users_role',
        'ix_users_tenant_id',
    ]:
        if _index_exists(conn, idx):
            op.drop_index(idx, table_name=None)

    # Drop uniques if they exist
    for tbl, con in [
        ('users', 'uq_users_email'),
        ('users', 'uq_users_username'),
        ('modules', 'uq_module_name'),
        ('roles', 'uq_roles_name'),
    ]:
        if _constraint_exists(conn, tbl, con):
            op.drop_constraint(con, tbl, type_='unique')
