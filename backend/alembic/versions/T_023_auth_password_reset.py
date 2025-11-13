"""Password reset + token revocation tables."""

from alembic import op
import sqlalchemy as sa


revision = "T_023_auth_password_reset"
down_revision = "T_022_notification_prefs_jsonb"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("user_agent", sa.String(length=256), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"])

    op.create_table(
        "revoked_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("reason", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_revoked_tokens_jti", "revoked_tokens", ["jti"])
    op.create_index("ix_revoked_tokens_user", "revoked_tokens", ["user_id"])
    op.create_index("ix_revoked_tokens_lookup", "revoked_tokens", ["user_id", "jti"])


def downgrade():
    op.drop_index("ix_revoked_tokens_lookup", table_name="revoked_tokens")
    op.drop_index("ix_revoked_tokens_lookup", table_name="revoked_tokens")
    op.drop_index("ix_revoked_tokens_user", table_name="revoked_tokens")
    op.drop_index("ix_revoked_tokens_jti", table_name="revoked_tokens")
    op.drop_table("revoked_tokens")
    op.drop_index("ix_password_reset_tokens_expires_at", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
