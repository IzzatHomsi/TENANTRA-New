"""
S-17: Add helpful indexes (idempotent).

- users(username) UNIQUE (if not already unique) and index on email
- audit_logs(user_id), audit_logs(timestamp)
- assets(tenant_id), assets(last_seen)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "e9f1a2b3c4d5"
down_revision = "d6e4f1a2b3c4"
branch_labels = None
depends_on = None

def upgrade():
    # users.username unique (if not already)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_users_username ON users (username)")
    # users.email index (case-insensitive search could use lower(email), but plain for now)
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    # audit_logs
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs (timestamp)")
    # assets
    op.execute("CREATE INDEX IF NOT EXISTS ix_assets_tenant_id ON assets (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_assets_last_seen ON assets (last_seen)")

def downgrade():
    # Safe drops with IF EXISTS
    op.execute("DROP INDEX IF EXISTS uq_users_username")
    op.execute("DROP INDEX IF EXISTS ix_users_email")
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_user_id")
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_timestamp")
    op.execute("DROP INDEX IF EXISTS ix_assets_tenant_id")
    op.execute("DROP INDEX IF EXISTS ix_assets_last_seen")
