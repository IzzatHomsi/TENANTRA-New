#!/usr/bin/env python3
"""
Seed the database with a default tenant and an admin user (idempotent).
Run inside the backend container:
    docker compose exec backend python -m app.scripts.db_seed
"""
import os
from app.database import SessionLocal
from app.models.user import User
from app.models.app_setting import AppSetting
from app.models.tenant import Tenant
from app.core.security import get_password_hash

DEFAULT_TENANT_NAME = os.getenv("SEED_TENANT_NAME", "Default Tenant")
DEFAULT_TENANT_SLUG = os.getenv("SEED_TENANT_SLUG", "default-tenant")
DEFAULT_ADMIN_USER = os.getenv("SEED_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASS = os.getenv("SEED_ADMIN_PASSWORD", "Admin@1234")
DEFAULT_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@tenantra.local")
DEFAULT_ADMIN_ROLE = os.getenv("SEED_ADMIN_ROLE", "admin")

def ensure_default_tenant(db):
    t = db.query(Tenant).filter(Tenant.name == DEFAULT_TENANT_NAME).first()
    if t:
        print(f"[seed] Tenant already exists: {t.name}")
        return t
    t = Tenant(
        name=DEFAULT_TENANT_NAME,
        slug=DEFAULT_TENANT_SLUG,
        is_active=True,
        storage_quota_gb=0,
    )
    db.add(t); db.commit(); db.refresh(t)
    print(f"[seed] Created tenant: {t.name} (id={t.id})")
    return t

def ensure_admin(db):
    u = db.query(User).filter(User.username == DEFAULT_ADMIN_USER).first()
    if u:
        # Backfill missing tenant_id or role if needed
        changed = False
        if not getattr(u, 'tenant_id', None):
            t = ensure_default_tenant(db)
            u.tenant_id = t.id
            changed = True
        if not getattr(u, 'role', None):
            u.role = DEFAULT_ADMIN_ROLE
            changed = True
        if changed:
            db.add(u); db.commit(); db.refresh(u)
            print(f"[seed] Admin '{u.username}' updated (tenant/role backfilled).")
        else:
            print(f"[seed] Admin '{u.username}' already exists — skipping.")
        return u
    t = ensure_default_tenant(db)
    u = User(
        username=DEFAULT_ADMIN_USER,
        password_hash=get_password_hash(DEFAULT_ADMIN_PASS),
        email=DEFAULT_ADMIN_EMAIL,
        is_active=True,
        tenant_id=t.id,
        role=DEFAULT_ADMIN_ROLE,
    )
    db.add(u); db.commit(); db.refresh(u)
    print(f"[seed] Created admin: {u.username}")
    return u

def main():
    db = SessionLocal()
    try:
        admin = ensure_admin(db)
        # Preseed global feature flags if not present
        if not db.query(AppSetting).filter(AppSetting.tenant_id.is_(None), AppSetting.key == "features").first():
            db.add(AppSetting(tenant_id=None, key="features", value={
                "notificationHistory": True,
                "auditLogs": True,
                "threatIntel": True,
                "featureFlags": True,
                "scanSchedules": True,
            }))
            db.commit()
        # Preseed tenant feature flags defaults for admin's tenant
        if admin and getattr(admin, "tenant_id", None):
            if not db.query(AppSetting).filter(AppSetting.tenant_id == admin.tenant_id, AppSetting.key == "features").first():
                db.add(AppSetting(tenant_id=admin.tenant_id, key="features", value={
                    "notificationHistory": True,
                    "auditLogs": True,
                    "threatIntel": True,
                    "scanSchedules": True,
                }))
                db.commit()
        print("[seed] Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
