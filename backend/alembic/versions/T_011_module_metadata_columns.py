"""Add extended metadata columns to modules."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "T_011_module_metadata_columns"
down_revision = "T_010_reencrypt_audit_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("modules", sa.Column("purpose", sa.Text(), nullable=True))
    op.add_column("modules", sa.Column("dependencies", sa.Text(), nullable=True))
    op.add_column("modules", sa.Column("preconditions", sa.Text(), nullable=True))
    op.add_column("modules", sa.Column("team", sa.String(length=150), nullable=True))
    op.add_column("modules", sa.Column("operating_systems", sa.String(length=255), nullable=True))
    op.add_column("modules", sa.Column("application_target", sa.String(length=255), nullable=True))
    op.add_column("modules", sa.Column("compliance_mapping", sa.Text(), nullable=True))
    op.add_column("modules", sa.Column("parameter_schema", sa.JSON(), nullable=True))
    op.create_index("ix_modules_category", "modules", ["category"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_modules_category", table_name="modules")
    op.drop_column("modules", "parameter_schema")
    op.drop_column("modules", "compliance_mapping")
    op.drop_column("modules", "application_target")
    op.drop_column("modules", "operating_systems")
    op.drop_column("modules", "team")
    op.drop_column("modules", "preconditions")
    op.drop_column("modules", "dependencies")
    op.drop_column("modules", "purpose")
