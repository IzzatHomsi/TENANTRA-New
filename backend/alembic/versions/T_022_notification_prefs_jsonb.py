"""Ensure notification_prefs JSON columns use native JSON/JSONB."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "T_022_notification_prefs_jsonb"
down_revision = "T_021_standardize_models"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.alter_column(
            "notification_prefs",
            "channels",
            type_=postgresql.JSONB(astext_type=sa.Text()),
            postgresql_using="channels::jsonb",
        )
        op.alter_column(
            "notification_prefs",
            "events",
            type_=postgresql.JSONB(astext_type=sa.Text()),
            postgresql_using="events::jsonb",
        )
    else:
        # SQLite/MySQL already store JSON as TEXT; no-op.
        pass


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.alter_column(
            "notification_prefs",
            "channels",
            type_=sa.JSON(),
            postgresql_using="channels::json",
        )
        op.alter_column(
            "notification_prefs",
            "events",
            type_=sa.JSON(),
            postgresql_using="events::json",
        )
