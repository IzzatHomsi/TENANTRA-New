"""Unify scheduled scans into scan_jobs."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "T_027_unify_scan_jobs"
down_revision = "T_026_module_enabled_flag"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {col["name"] for col in inspector.get_columns("scan_jobs")}

    def _ensure_column(name: str, column: sa.Column):
        if name in existing:
            return
        op.add_column("scan_jobs", column)
        existing.add(name)

    _ensure_column("module_id", sa.Column("module_id", sa.Integer(), nullable=True))
    _ensure_column("agent_id", sa.Column("agent_id", sa.Integer(), nullable=True))
    _ensure_column("parameters", sa.Column("parameters", sa.JSON(), nullable=True))
    _ensure_column(
        "enabled",
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    _ensure_column("next_run_at", sa.Column("next_run_at", sa.DateTime(), nullable=True))
    _ensure_column("last_run_at", sa.Column("last_run_at", sa.DateTime(), nullable=True))
    _ensure_column(
        "updated_at",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    fk_names = {fk["name"] for fk in inspector.get_foreign_keys("scan_jobs")}
    if "fk_scan_jobs_module_id" not in fk_names:
        op.create_foreign_key(
            "fk_scan_jobs_module_id",
            "scan_jobs",
            "modules",
            ["module_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if "fk_scan_jobs_agent_id" not in fk_names:
        op.create_foreign_key(
            "fk_scan_jobs_agent_id",
            "scan_jobs",
            "agents",
            ["agent_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.execute(
        """
        INSERT INTO scan_jobs (
            tenant_id,
            name,
            description,
            scan_type,
            priority,
            schedule,
            status,
            created_by,
            created_at,
            started_at,
            completed_at,
            module_id,
            agent_id,
            parameters,
            enabled,
            next_run_at,
            last_run_at,
            updated_at
        )
        SELECT
            tenant_id,
            COALESCE('Module #' || module_id, 'Module schedule'),
            'Migrated scheduled scan',
            'module',
            'normal',
            cron_expr,
            status,
            NULL,
            COALESCE(created_at, CURRENT_TIMESTAMP),
            last_run_at,
            NULL,
            module_id,
            agent_id,
            parameters,
            enabled,
            next_run_at,
            last_run_at,
            COALESCE(updated_at, CURRENT_TIMESTAMP)
        FROM scheduled_scans
        """
    )

    op.drop_table("scheduled_scans")


def downgrade():
    op.create_table(
        "scheduled_scans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("modules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cron_expr", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="scheduled"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.execute(
        """
        INSERT INTO scheduled_scans (
            id,
            tenant_id,
            module_id,
            agent_id,
            cron_expr,
            status,
            enabled,
            parameters,
            last_run_at,
            next_run_at,
            created_at,
            updated_at
        )
        SELECT
            id,
            tenant_id,
            module_id,
            agent_id,
            schedule,
            status,
            enabled,
            parameters,
            last_run_at,
            next_run_at,
            created_at,
            updated_at
        FROM scan_jobs
        WHERE scan_type = 'module'
        """
    )

    op.drop_constraint("fk_scan_jobs_module_id", "scan_jobs", type_="foreignkey")
    op.drop_constraint("fk_scan_jobs_agent_id", "scan_jobs", type_="foreignkey")
    op.drop_column("scan_jobs", "module_id")
    op.drop_column("scan_jobs", "agent_id")
    op.drop_column("scan_jobs", "parameters")
    op.drop_column("scan_jobs", "enabled")
    op.drop_column("scan_jobs", "next_run_at")
    op.drop_column("scan_jobs", "last_run_at")
    op.drop_column("scan_jobs", "updated_at")
