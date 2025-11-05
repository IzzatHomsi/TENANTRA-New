"""
S-15: Tenant-aware CORS origins table.

Creates table:
- tenant_cors_origins (
    id SERIAL PK,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    origin TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    is_global BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL
  )
Unique:
- (tenant_id, origin)
Indexes:
- (origin)
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = "d6e4f1a2b3c4"
down_revision = "c41a5d2e7f10"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "tenant_cors_origins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("is_global", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
    )
    op.create_unique_constraint("uq_tenant_origin", "tenant_cors_origins", ["tenant_id", "origin"])
    op.create_index("ix_tenant_cors_origin", "tenant_cors_origins", ["origin"])

def downgrade():
    op.drop_index("ix_tenant_cors_origin", table_name="tenant_cors_origins")
    op.drop_constraint("uq_tenant_origin", "tenant_cors_origins", type_="unique")
    op.drop_table("tenant_cors_origins")
