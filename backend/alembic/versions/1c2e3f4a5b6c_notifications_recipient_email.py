"""add recipient_email to notifications"""

from alembic import op
import sqlalchemy as sa

revision = "1c2e3f4a5b6c"
down_revision = "0e3a0b0f0fcf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("recipient_email", sa.String(length=255), nullable=True))
    op.execute("UPDATE notifications SET recipient_email = COALESCE(recipient_email, 'pending@tenantra.local')")
    op.alter_column("notifications", "recipient_email", nullable=False)
    op.alter_column("notifications", "recipient_id", existing_type=sa.Integer(), nullable=True)
    op.drop_constraint("notifications_recipient_id_fkey", "notifications", type_="foreignkey")
    op.create_foreign_key(
        "notifications_recipient_id_fkey",
        "notifications",
        "users",
        ["recipient_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("notifications_recipient_id_fkey", "notifications", type_="foreignkey")
    op.create_foreign_key(
        "notifications_recipient_id_fkey",
        "notifications",
        "users",
        ["recipient_id"],
        ["id"],
    )
    op.alter_column("notifications", "recipient_id", existing_type=sa.Integer(), nullable=False)
    op.drop_column("notifications", "recipient_email")
