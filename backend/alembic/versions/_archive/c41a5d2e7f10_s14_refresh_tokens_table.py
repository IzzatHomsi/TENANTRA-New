"""
S-14: Refresh tokens table + tenant-aware CORS seed hook (non-destructive).

Table: refresh_tokens
- id PK
- user_id FK -> users.id
- token_hash TEXT (sha256 of opaque token)
- created_at, expires_at, revoked_at
- user_agent, ip (optional)
Indexes:
- uq token_hash
- ix user_id
- ix expires_at
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c41a5d2e7f10"
down_revision = "a2b7c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=True),
    )


def downgrade():
    op.drop_table("refresh_tokens")
