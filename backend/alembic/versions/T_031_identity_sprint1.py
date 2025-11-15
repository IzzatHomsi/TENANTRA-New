"""Identity Sprint 1: email verification + tenant join requests."""

from alembic import op
import sqlalchemy as sa


revision = "T_031_identity_sprint1"
down_revision = "T_030_module_agent_mapping_table"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE users SET email_verified_at = timezone('utc', now()) WHERE email_verified_at IS NULL")

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("user_agent", sa.String(length=256), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_email_verification_tokens_expires_at", "email_verification_tokens", ["expires_at"])

    op.create_table(
        "tenant_join_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("decision_note", sa.Text(), nullable=True),
        sa.Column("decision_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("decision_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("timezone('utc', now())")),
    )
    op.create_index("ix_tenant_join_requests_tenant", "tenant_join_requests", ["tenant_id"])
    op.create_index("ix_tenant_join_requests_status", "tenant_join_requests", ["status"])


def downgrade():
    op.drop_index("ix_tenant_join_requests_status", table_name="tenant_join_requests")
    op.drop_index("ix_tenant_join_requests_tenant", table_name="tenant_join_requests")
    op.drop_table("tenant_join_requests")

    op.drop_index("ix_email_verification_tokens_expires_at", table_name="email_verification_tokens")
    op.drop_table("email_verification_tokens")

    op.drop_column("users", "email_verified_at")
