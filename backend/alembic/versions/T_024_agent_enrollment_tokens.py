"""Agent enrollment tokens for self-registration."""

from alembic import op
import sqlalchemy as sa


revision = "T_024_agent_enrollment_tokens"
down_revision = "T_023_auth_password_reset"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "agent_enrollment_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False, unique=True),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("timezone('utc', now())")),
    )
    op.create_index("ix_agent_enrollment_tokens_tenant", "agent_enrollment_tokens", ["tenant_id"])
    op.create_index("ix_agent_enrollment_tokens_expires_at", "agent_enrollment_tokens", ["expires_at"])


def downgrade():
    op.drop_index("ix_agent_enrollment_tokens_expires_at", table_name="agent_enrollment_tokens")
    op.drop_index("ix_agent_enrollment_tokens_tenant", table_name="agent_enrollment_tokens")
    op.drop_table("agent_enrollment_tokens")
