"""Module management API endpoints."""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.module import Module
from app.models.tenant_module import TenantModule
from app.models.user import User
from app.services.module_registry import (
    get_parameter_schema_for_module,
    get_runner_for_module,
)
from app.utils.rbac import role_required

router = APIRouter(prefix="/modules", tags=["Modules"])


def _serialize_module(module: Module, enabled: bool) -> Dict[str, object]:
    last_update = module.last_update.isoformat() if module.last_update else None
    schema = module.parameter_schema or get_parameter_schema_for_module(module)
    runner_available = get_runner_for_module(module) is not None
    return {
        "id": module.id,
        "external_id": module.external_id,
        "name": module.name,
        "category": module.category,
        "phase": module.phase,
        "impact_level": module.impact_level,
        "path": module.path,
        "status": module.status,
        "checksum": module.checksum,
        "description": module.description,
        "purpose": module.purpose,
        "dependencies": module.dependencies,
        "preconditions": module.preconditions,
        "team": module.team,
        "operating_systems": module.operating_systems,
        "application_target": module.application_target,
        "compliance_mapping": module.compliance_mapping,
        "parameter_schema": schema or {},
        "has_runner": runner_available,
        "enabled": enabled,
        "enabled_global": module.is_effectively_enabled,
        "last_update": last_update,
    }


@router.get("/")
def list_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, object]]:
    modules = db.query(Module).all()
    overrides = {}
    if current_user.tenant_id:
        rows = (
            db.query(TenantModule)
            .filter(TenantModule.tenant_id == current_user.tenant_id)
            .all()
        )
        overrides = {row.module_id: row.enabled for row in rows}

    result: List[Dict[str, object]] = []
    for module in modules:
        base_enabled = module.is_effectively_enabled
        override = overrides.get(module.id)
        effective = bool(override) if override is not None else base_enabled
        result.append(_serialize_module(module, effective))
    return result


@router.put("/{module_id}", dependencies=[Depends(role_required("admin", "super_admin"))])
def set_module_enabled(
    module_id: int,
    data: Dict[str, object],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, object]:
    if "enabled" not in data:
        raise HTTPException(status_code=400, detail="'enabled' field is required")
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    enabled = bool(data["enabled"])
    tenant_module = (
        db.query(TenantModule)
        .filter(
            TenantModule.tenant_id == current_user.tenant_id,
            TenantModule.module_id == module_id,
        )
        .first()
    )
    if tenant_module:
        tenant_module.enabled = enabled
    else:
        tenant_module = TenantModule(
            tenant_id=current_user.tenant_id,
            module_id=module_id,
            enabled=enabled,
        )
        db.add(tenant_module)
    db.commit()
    return _serialize_module(module, enabled)


@router.post("/", dependencies=[Depends(role_required("admin", "super_admin"))])
def create_module(
    data: Dict[str, object],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, object]:
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="'name' is required")

    existing = db.query(Module).filter(Module.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Module name already exists")

    phase_raw = data.get("phase")
    if phase_raw is not None and phase_raw != "":
        try:
            phase_value = int(phase_raw)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid phase value")
    else:
        phase_value = None

    module = Module(
        name=name,
        external_id=data.get("external_id"),
        category=data.get("category"),
        phase=phase_value,
        impact_level=data.get("impact_level"),
        path=data.get("path"),
        status=data.get("status"),
        checksum=data.get("checksum"),
        description=data.get("description"),
        purpose=data.get("purpose"),
        dependencies=data.get("dependencies"),
        preconditions=data.get("preconditions"),
        team=data.get("team"),
        operating_systems=data.get("operating_systems"),
        application_target=data.get("application_target"),
        compliance_mapping=data.get("compliance_mapping"),
        enabled=bool(data.get("enabled", True)),
    )

    parameter_schema = data.get("parameter_schema")
    if isinstance(parameter_schema, dict):
        module.parameter_schema = parameter_schema

    last_update = data.get("last_update")
    if isinstance(last_update, str) and last_update.strip():
        try:
            module.last_update = datetime.fromisoformat(last_update.strip())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid last_update format (expected ISO 8601)")

    db.add(module)
    db.commit()
    db.refresh(module)
    return _serialize_module(module, module.is_effectively_enabled)
