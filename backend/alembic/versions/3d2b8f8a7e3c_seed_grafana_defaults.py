"""ensure grafana app settings defaults exist"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

# revision identifiers, used by Alembic.
revision = "3d2b8f8a7e3c"
down_revision = "T_021_standardize_models"
branch_labels = None
depends_on = None


DEFAULTS = {
    "grafana.url": None,
    "grafana.dashboard_uid": "tenantra-overview",
    "grafana.datasource_uid": None,
    "grafana.proxy.max_body_bytes": 1 * 1024 * 1024,
    "grafana.proxy.max_requests_per_minute": 60,
}


def upgrade() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()
    app_settings = sa.Table("app_settings", metadata, autoload_with=bind)
    session = orm.Session(bind=bind)
    try:
        for key, value in DEFAULTS.items():
            exists = session.execute(
                sa.select(app_settings.c.id).where(
                    app_settings.c.tenant_id.is_(None),
                    app_settings.c.key == key,
                )
            ).first()
            if not exists:
                session.execute(
                    app_settings.insert().values(
                        tenant_id=None,
                        key=key,
                        value=value,
                    )
                )
        session.commit()
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()
    app_settings = sa.Table("app_settings", metadata, autoload_with=bind)
    session = orm.Session(bind=bind)
    try:
        session.execute(
            app_settings.delete().where(
                app_settings.c.tenant_id.is_(None),
                app_settings.c.key.in_(list(DEFAULTS.keys())),
            )
        )
        session.commit()
    finally:
        session.close()
