from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.module import Module
from app.models.tenant_module import TenantModule
from app.models.user import User

router = APIRouter(prefix="/admin/modules", tags=["Admin Modules"])


def _serialize(module: Module, enabled: bool) -> Dict[str, object]:
    return {
        "id": module.id,
        "name": module.name,
        "category": module.category,
        "phase": module.phase,
        "enabled": enabled,
    }


@router.get("", response_model=List[Dict[str, object]])
def list_modules_admin(db: Session = Depends(get_db), user: User = Depends(get_admin_user)) -> List[Dict[str, object]]:
    modules = db.query(Module).all()
    overrides = {r.module_id: r.enabled for r in db.query(TenantModule).filter(TenantModule.tenant_id == user.tenant_id).all()}
    out: List[Dict[str, object]] = []
    for m in modules:
        base = bool(getattr(m, 'enabled', True)) if hasattr(m, 'enabled') else m.is_effectively_enabled
        eff = overrides.get(m.id)
        enabled = bool(eff) if eff is not None else base
        out.append(_serialize(m, enabled))
    return out


@router.put("/bulk", response_model=Dict[str, int])
def bulk_set_modules(
    payload: Dict[str, List[int]],
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user),
) -> Dict[str, int]:
    enable_ids = set(payload.get("enable", []) or [])
    disable_ids = set(payload.get("disable", []) or [])
    changed = 0
    for module_id in (enable_ids | disable_ids):
        target = (
            db.query(TenantModule)
            .filter(TenantModule.tenant_id == user.tenant_id, TenantModule.module_id == module_id)
            .first()
        )
        val = module_id in enable_ids
        if target:
            if target.enabled != val:
                target.enabled = val
                changed += 1
        else:
            db.add(TenantModule(tenant_id=user.tenant_id, module_id=module_id, enabled=val))
            changed += 1
    db.commit()
    return {"changed": changed}


@router.post("/seed", response_model=Dict[str, int], status_code=status.HTTP_201_CREATED)
def seed_modules_from_csv(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> Dict[str, int]:
    """Admin action to import modules from the CSV mapped under /app/docs/modules.

    It is safe to call multiple times; existing modules are updated/deduped by importer.
    """
    try:
        # Prefer robust importer when available
        try:
            from app.scripts.import_modules_from_csv import import_modules as _import_modules  # type: ignore
        except Exception:
            from scripts.import_modules_from_csv import import_modules as _import_modules  # type: ignore
        from pathlib import Path
        candidates = [
            Path('/app/docs/modules/Tenantra_Module_Backlog_PhaseLinked_v8.csv'),
            Path('docs/modules/Tenantra_Module_Backlog_PhaseLinked_v8.csv'),
        ]
        csv_path = next((p for p in candidates if p.exists()), None)
        if not csv_path:
            raise HTTPException(status_code=404, detail='CSV not found in /app/docs/modules')
        stats = _import_modules(csv_path)
        # Ensure Port Scan demo exists for convenience
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
            )
            db.add(demo)
            db.commit()
        # Ensure DB session sees updates from importer (it uses its own SessionLocal)
        db.expire_all()
        return {"created": int(stats.get("created", 0)), "updated": int(stats.get("updated", 0)), "rows": int(stats.get("rows", 0))}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/create-port-scan", response_model=Dict[str, int], status_code=status.HTTP_201_CREATED)
def create_port_scan_module(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> Dict[str, int]:
    """Create a minimal 'Networking — Port Scan' module if not present.

    Useful for minimal deployments without the CSV data.
    """
    from app.models.module import Module as _Module
    existing = db.query(_Module).filter(_Module.external_id == 'port-scan').first()
    if existing:
        return {"created": 0}
    module = _Module(
        external_id='port-scan',
        name='Networking — Port Scan',
        category='Networking',
        phase=1,
        status='active',
        enabled=True,
        description='Quick TCP port reachability scan with banner/TLS capture.',
    )
    db.add(module)
    db.commit(); db.refresh(module)
    return {"created": 1}
