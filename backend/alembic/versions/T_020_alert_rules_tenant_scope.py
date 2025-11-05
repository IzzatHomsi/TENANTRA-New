"""Add tenant scoping to alert rules."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "T_020_alert_rules_tenant_scope"
down_revision: Union[str, None] = "T_019_notification_prefs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("alert_rules", sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.create_index("ix_alert_rules_tenant_id", "alert_rules", ["tenant_id"], unique=False)
    op.create_foreign_key(
        "fk_alert_rules_tenants",
        "alert_rules",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE alert_rules SET tenant_id = 1 WHERE tenant_id IS NULL"))
    op.alter_column("alert_rules", "tenant_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_alert_rules_tenants", "alert_rules", type_="foreignkey")
    op.drop_index("ix_alert_rules_tenant_id", table_name="alert_rules")
    op.drop_column("alert_rules", "tenant_id")
