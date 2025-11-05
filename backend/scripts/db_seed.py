"""
Robust DB seed:
- Ensures roles ('admin', 'standard_user') exist
- Creates/updates an admin user from env or sane defaults

Run inside container:
    # either:
    python /app/scripts/db_seed.py
    # or (recommended):
    python -m app.scripts.db_seed
"""

# --- bootstrap PYTHONPATH so "from app.*" works even when run as a file ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent  # -> /app
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# --- end bootstrap ---

import os
import copy
from datetime import datetime
import subprocess  # nosec B404: controlled use of subprocess for Alembic CLI
import shutil
import traceback

from sqlalchemy.orm import Session

import os as _os
import sys as _sys
import pathlib as _pathlib
from typing import Optional

from app.database import SessionLocal

# Diagnostics: print runtime import context early to help CI debugging
try:
    print("db_seed runtime diagnostics:")
    print("cwd:", _os.getcwd())
    print("__file__:", __file__)
    print("sys.path:")
    for p in _sys.path:
        print("  ", p)
    models_dir = _pathlib.Path(__file__).resolve().parents[1] / "app" / "models"
    print("listing app/models (exists={}):".format(models_dir.exists()))
    if models_dir.exists():
        for f in sorted(models_dir.glob("*.py")):
            print("  -", f.name)
except Exception as _e:
    print("Failed writing diagnostics:", _e)

try:
    from app.models.user import User
    from app.models.tenant import Tenant
    from app.models.tenant_cors_origin import TenantCORSOrigin
    from app.models.role import Role
    from app.models.app_setting import AppSetting
except ModuleNotFoundError as _mnfe:
    print("ModuleNotFoundError during imports in db_seed:", _mnfe)
    print("sys.path at failure:")
    for p in _sys.path:
        print("  ", p)
    # list the package tree so we can see what files are present in CI
    try:
        root = _pathlib.Path(__file__).resolve().parents[1] / "app"
        for p in sorted(root.rglob("*.py")):
            print("FS:", p.relative_to(root.parent))
    except Exception:
        pass
    raise

from app.core.security import get_password_hash, verify_password

DEFAULT_ADMIN_USER = os.getenv("SEED_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
DEFAULT_ADMIN_PASS = os.getenv("SEED_ADMIN_PASSWORD", "Admin@1234")
DEFAULT_TENANT_ID = int(os.getenv("SEED_ADMIN_TENANT_ID", "1"))


def _parse_bool(value: Optional[str], default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def ensure_role(db: Session, name: str) -> None:
    if not db.query(Role).filter(Role.name == name).first():
        db.add(Role(name=name))
        db.commit()


def ensure_admin(db: Session) -> None:
    u = db.query(User).filter(User.username == DEFAULT_ADMIN_USER).first()
    if not u:
        u = User(
            username=DEFAULT_ADMIN_USER,
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=get_password_hash(DEFAULT_ADMIN_PASS),
            role="admin",
            tenant_id=DEFAULT_TENANT_ID,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(u)
        db.commit()
    else:
        changed = False
        if u.role != "admin":
            u.role = "admin"
            changed = True
        if not u.is_active:
            u.is_active = True
            changed = True
        if not verify_password(DEFAULT_ADMIN_PASS, u.password_hash):
            u.password_hash = get_password_hash(DEFAULT_ADMIN_PASS)
            changed = True
        if changed:
            u.updated_at = datetime.utcnow()
            db.commit()


def main():
    # Try to ensure migrations are applied first to avoid 'relation does not exist' errors
    try:
        print("Ensuring database migrations are applied (alembic upgrade head)")
        alembic_exe = shutil.which("alembic")
        if not alembic_exe:
            raise RuntimeError("alembic not found in PATH")
        proc = subprocess.run([alembic_exe, "upgrade", "head"], check=False)  # nosec B603: fixed path, no shell
        if proc.returncode != 0:
            print("alembic upgrade head failed with exit code", proc.returncode)
            print("Failing seed to avoid running against an out-of-date DB.")
            raise SystemExit(proc.returncode)
    except SystemExit:
        raise
    except Exception:
        print("Warning: failed to run alembic upgrade head from seed script; continuing and will fail gracefully if DB is missing tables.")

    db = SessionLocal()
    try:
        # Ensure a default tenant exists
        tenant = None
        try:
            tenant = db.query(Tenant).filter(Tenant.id == DEFAULT_TENANT_ID).first()
        except Exception:
            print("DB query failed while checking tenant; this likely means migrations haven't been applied yet.")
            print(traceback.format_exc())
            # Re-raise so CI will catch it unless we can continue safely
            raise
        if not tenant:
            tenant = Tenant(id=DEFAULT_TENANT_ID, name="Default Tenant", slug="default", is_active=True)
            db.add(tenant)
            db.commit()

        try:
            ensure_role(db, "admin")
            ensure_role(db, "standard_user")
        except Exception:
            print("Failed to ensure roles exist; roles table may be missing. Printing traceback:")
            print(traceback.format_exc())
            raise
        ensure_admin(db)
        # Import/refresh modules from the backlog CSV (respect override env)
        try:
            import_modules_flag = os.getenv("TENANTRA_IMPORT_MODULES", "1").strip().lower()
            if import_modules_flag in {"1", "true", "yes", "on"}:
                from pathlib import Path as _Path
                try:
                    try:
                        from app.scripts.import_modules_from_csv import import_modules as _import_modules
                    except Exception:
                        from scripts.import_modules_from_csv import import_modules as _import_modules  # type: ignore
                    csv_path = _Path("docs/modules/Tenantra_Module_Backlog_PhaseLinked_v8.csv")
                    if csv_path.exists():
                        stats = _import_modules(csv_path)
                        print(f"[seed] Imported modules: {stats}")
                except Exception:
                    # Fallback to simple seeder
                    try:
                        from app.scripts.seed_modules_from_csv import seed_modules_from_csv as _seed_simple
                    except Exception:
                        from scripts.seed_modules_from_csv import seed_modules_from_csv as _seed_simple  # type: ignore
                    _ = _seed_simple(db)
        except Exception:
            print("Module import during seed failed; continuing without aborting.")
            traceback.print_exc()
        # Seed a demo Port Scan module if not present for easy demos
        try:
            from app.models.module import Module as _Module
            demo = db.query(_Module).filter(_Module.external_id == 'port-scan').first()
            if not demo:
                demo = _Module(
                    external_id='port-scan',
                    name='Networking — Port Scan',
                    category='Networking',
                    phase=1,
                    status='active',
                    enabled=True,
                    description='Quick TCP port reachability scan with banner/TLS capture.',
                    parameter_schema={
                        'type':'object',
                        'properties':{
                            'host': {'type':'string','description':'Target host (IP or DNS)'},
                            'ports': {'type':'array','items':{'type':'integer'},'description':'Ports to check, e.g., [22,80,443]'},
                            'capture_banner': {'type':'boolean','default': True},
                            'tls_probe': {'type':'boolean','default': True}
                        }
                    },
                )
                db.add(demo)
                db.commit()
        except Exception:
            pass

        # Seed AWS IAM Baseline (Phase 2) to appear in catalog
        try:
            from app.models.module import Module as _Module
            iam = db.query(_Module).filter(_Module.external_id == 'aws-iam-baseline').first()
            if not iam:
                iam = _Module(
                    external_id='aws-iam-baseline',
                    name='AWS IAM Baseline',
                    category='Identity & Access Scanning',
                    phase=2,
                    status='active',
                    enabled=True,
                    description='Checks MFA and key age against baseline policy.',
                    parameter_schema={
                        'type': 'object',
                        'properties': {
                            'users': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'username': {'type': 'string'},
                                        'mfa_enabled': {'type': 'boolean'},
                                        'access_keys': {
                                            'type': 'array',
                                            'items': {
                                                'type': 'object',
                                                'properties': {
                                                    'age_days': {'type': 'integer'},
                                                    'active': {'type': 'boolean'},
                                                },
                                                'required': ['age_days','active']
                                            },
                                            'default': []
                                        }
                                    },
                                    'required': ['username','mfa_enabled']
                                },
                                'default': []
                            },
                            'max_key_age_days': {'type':'integer','default': 90},
                            'require_mfa': {'type':'boolean','default': True}
                        }
                    },
                )
                db.add(iam)
                db.commit()
        except Exception:
            pass

        # Configure DHCP source defaults from env (Infoblox or HTTP API)
        timeout_raw = os.getenv('TENANTRA_DHCP_SOURCE_TIMEOUT') or ''
        try:
            timeout_value = float(timeout_raw) if timeout_raw else 10.0
        except ValueError:
            timeout_value = 10.0
        dhcp_source_default = {
            'type': os.getenv('TENANTRA_DHCP_SOURCE_TYPE', 'manual'),
            'endpoint': os.getenv('TENANTRA_DHCP_SOURCE_ENDPOINT'),
            'username': os.getenv('TENANTRA_DHCP_SOURCE_USERNAME'),
            'password': os.getenv('TENANTRA_DHCP_SOURCE_PASSWORD'),
            'api_key': os.getenv('TENANTRA_DHCP_SOURCE_API_KEY'),
            'verify_tls': _parse_bool(os.getenv('TENANTRA_DHCP_SOURCE_VERIFY_TLS'), True),
            'timeout_seconds': timeout_value,
        }
        # Ensure empty strings become None for cleanliness
        for _key in list(dhcp_source_default.keys()):
            if isinstance(dhcp_source_default[_key], str) and not dhcp_source_default[_key]:
                dhcp_source_default[_key] = None

        # Seed default global app settings if missing
        defaults = {
            'theme.colors.primary': '#0ea5e9',
            'grafana.url': 'http://grafana:3000',
            'networking.plan.targets': [
                { 'host': 'backend', 'ports': [5000] },
                { 'host': 'grafana', 'ports': [3000] },
            ],
            'networking.dhcp.scopes': [
                {
                    'name': 'HQ-Data',
                    'total_leases': 512,
                    'active_leases': 220,
                    'reserved_leases': 16,
                    'dhcp_server': 'infoblox-hq01',
                    'site': 'HQ',
                    'vlan': '10',
                    'tags': ['production', 'hq'],
                },
                {
                    'name': 'Branch-01',
                    'total_leases': 256,
                    'active_leases': 120,
                    'reserved_leases': 8,
                    'dhcp_server': 'infoblox-branch01',
                    'site': 'Branch-01',
                    'vlan': '120',
                    'tags': ['branch'],
                },
            ],
            'networking.dhcp.source': {
                **dhcp_source_default,
            },
        }
        for k, v in defaults.items():
            row = db.query(AppSetting).filter(AppSetting.tenant_id.is_(None), AppSetting.key == k).first()
            if not row:
                db.add(AppSetting(tenant_id=None, key=k, value=v))
        db.commit()
        # Ensure each tenant has DHCP scope defaults seeded
        dhcp_scope_key = 'networking.dhcp.scopes'
        dhcp_source_key = 'networking.dhcp.source'
        tenants = db.query(Tenant).all()
        for tenant_row in tenants:
            scope_row = (
                db.query(AppSetting)
                .filter(AppSetting.tenant_id == tenant_row.id, AppSetting.key == dhcp_scope_key)
                .first()
            )
            if not scope_row:
                scope_value = copy.deepcopy(defaults[dhcp_scope_key])
                db.add(AppSetting(tenant_id=tenant_row.id, key=dhcp_scope_key, value=scope_value))
            source_row = (
                db.query(AppSetting)
                .filter(AppSetting.tenant_id == tenant_row.id, AppSetting.key == dhcp_source_key)
                .first()
            )
            if not source_row:
                source_value = copy.deepcopy(defaults[dhcp_source_key])
                db.add(AppSetting(tenant_id=tenant_row.id, key=dhcp_source_key, value=source_value))
        db.commit()
        # Ensure a local CORS origin exists for the default tenant to support dev/testing
        origin = "http://localhost"
        existing = (
            db.query(TenantCORSOrigin)
            .filter(TenantCORSOrigin.tenant_id == tenant.id, TenantCORSOrigin.origin == origin)
            .first()
        )
        if not existing:
            db.add(TenantCORSOrigin(tenant_id=tenant.id, origin=origin, enabled=True, is_global=False))
            db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

