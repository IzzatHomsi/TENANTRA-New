"""extend modules table with csv metadata"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0e3a0b0f0fcf"
down_revision = "T_009_agent_is_active"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("modules", sa.Column("external_id", sa.String(length=64), nullable=True))
    op.add_column("modules", sa.Column("phase", sa.Integer(), nullable=True))
    op.add_column("modules", sa.Column("impact_level", sa.String(length=50), nullable=True))
    op.add_column("modules", sa.Column("path", sa.String(length=255), nullable=True))
    op.add_column("modules", sa.Column("status", sa.String(length=50), nullable=True))
    op.add_column("modules", sa.Column("checksum", sa.String(length=128), nullable=True))
    op.add_column("modules", sa.Column("last_update", sa.DateTime(), nullable=True))
    op.create_unique_constraint("uq_modules_external_id", "modules", ["external_id"])
    op.create_index("ix_modules_phase", "modules", ["phase"], unique=False)
    op.execute(
        "UPDATE modules SET status = 'active' WHERE status IS NULL"
    )


def downgrade() -> None:
    op.drop_index("ix_modules_phase", table_name="modules")
    op.drop_constraint("uq_modules_external_id", "modules", type_="unique")
    op.drop_column("modules", "last_update")
    op.drop_column("modules", "checksum")
    op.drop_column("modules", "status")
    op.drop_column("modules", "path")
    op.drop_column("modules", "impact_level")
    op.drop_column("modules", "phase")
    op.drop_column("modules", "external_id")
