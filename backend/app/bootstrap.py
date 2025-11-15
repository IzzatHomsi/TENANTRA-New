"""Application bootstrap logic for Tenantra."""

from __future__ import annotations

import logging
import os
from datetime import datetime

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import get_password_hash, verify_password
from app.core.admin_passwords import resolve_admin_password
from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.module import Module, ModuleStatus
from app.models.notification_pref import NotificationPreference  # noqa: F401
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.user import User
from app.models.app_setting import AppSetting

logger = logging.getLogger("tenantra.bootstrap")


def bootstrap_test_data() -> None:
    """Create tables and seed minimal data for testing."""
    try:
        if (
            os.getenv("TENANTRA_TEST_BOOTSTRAP", "0").strip().lower()
            in {"1", "true", "yes", "on"}
            or os.getenv("PYTEST_CURRENT_TEST")
        ):
            # For test bootstrap we create the full schema to satisfy tests
            # across modules without requiring Alembic migrations.
            try:
                # Ensure all model modules are imported so Base.metadata knows every table/column
                import app.models  # noqa: F401
            except Exception:
                logger.debug("Unable to import app.models during bootstrap", exc_info=True)
            try:
                Base.metadata.create_all(bind=engine)
            except Exception:
                # Fallback: if create_all raises, try conditional create
                insp = inspect(engine)
                needed = {"users", "tenants", "roles"}
                existing = set(insp.get_table_names())
                if not needed.issubset(existing):
                    Base.metadata.create_all(bind=engine)
            try:
                AppSetting.__table__.create(bind=engine, checkfirst=True)
            except SQLAlchemyError:
                logger.debug("Unable to ensure app_settings table exists", exc_info=True)

            # Seed minimal data
            db = SessionLocal()
            try:
                _ensure_app_settings(db)
                if not db.query(Role).filter(Role.name == "admin").first():
                    db.add(Role(name="admin"))
                    db.commit()
                if not db.query(Role).filter(Role.name == "standard_user").first():
                    db.add(Role(name="standard_user"))
                    db.commit()

                tenant = db.query(Tenant).filter(Tenant.id == 1).first()
                if not tenant:
                    tenant = Tenant(id=1, name="Default", slug="default", is_active=True)
                    db.add(tenant)
                    db.commit()

                admin_user = db.query(User).filter(User.username == "admin").first()
                admin_password = os.getenv("TENANTRA_ADMIN_PASSWORD")
                if not admin_password:
                    raise RuntimeError("TENANTRA_ADMIN_PASSWORD environment variable not set for bootstrap.")
                if not admin_user:
                    admin_user = User(
                        username="admin",
                        email="admin@example.com",
                        password_hash=get_password_hash(admin_password),
                        role="admin",
                        tenant_id=1,
                        is_active=True,
                    )
                    admin_user.email_verified_at = datetime.utcnow()
                    db.add(admin_user)
                    db.commit()
                else:
                    # Ensure baseline properties for repeatable tests
                    changed = False
                    if not verify_password(admin_password, admin_user.password_hash):
                        admin_user.password_hash = get_password_hash(admin_password)
                        changed = True
                    if admin_user.role != "admin":
                        admin_user.role = "admin"
                        changed = True
                    if not admin_user.is_active:
                        admin_user.is_active = True
                        changed = True
                    if admin_user.tenant_id != 1:
                        admin_user.tenant_id = 1
                        changed = True
                    if not admin_user.email_verified_at:
                        admin_user.email_verified_at = datetime.utcnow()
                        changed = True
                    if changed:
                        db.commit()

                # Ensure core test modules exist so module-run tests can find them by name
                mods = [
                    {
                        "name": "cis_benchmark",
                        "category": "Security Compliance",
                        "status": ModuleStatus.ACTIVE,
                        "enabled": True,
                    },
                    {
                        "name": "pci_dss_check",
                        "category": "Security Compliance",
                        "status": ModuleStatus.ACTIVE,
                        "enabled": True,
                    },
                ]
                for m in mods:
                    if not db.query(Module).filter(Module.name == m["name"]).first():
                        db.add(Module(**m))
                        db.commit()
            finally:
                db.close()
            logger.info("Test bootstrap completed (tables created and admin seeded).")
    except Exception:
        logger.exception("Test bootstrap failed.")


def _ensure_app_settings(db):
    defaults = [
        {"tenant_id": None, "key": "site.name", "value": "Tenantra"},
        {"tenant_id": None, "key": "grafana.url", "value": "/grafana"},
        {"tenant_id": None, "key": "grafana.dashboard_uid", "value": "tenantra-overview"},
        {"tenant_id": None, "key": "grafana.datasource_uid", "value": "tenantra-prom"},
        {"tenant_id": None, "key": "features", "value": {"agent_management": True, "compliance": True}},
    ]
    changed = False
    for entry in defaults:
        query = db.query(AppSetting).filter(AppSetting.key == entry["key"])
        if entry["tenant_id"] is None:
            query = query.filter(AppSetting.tenant_id.is_(None))
        else:
            query = query.filter(AppSetting.tenant_id == entry["tenant_id"])
        if not query.first():
            db.add(AppSetting(**entry))
            changed = True
    if changed:
        db.commit()
