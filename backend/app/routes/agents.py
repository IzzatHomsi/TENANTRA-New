"""Agent API endpoints."""

import secrets
from typing import Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.agent import Agent
from app.models.module import Module
from app.models.tenant_module import TenantModule
from app.models.user import User
from app.utils.rbac import role_required

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/enroll")
def enroll_agent(
    name: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("admin", "super_admin")),
) -> Dict[str, str]:
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Agent name is required")
    token = secrets.token_hex(16)
    agent = Agent(name=name.strip(), token=token, tenant_id=current_user.tenant_id)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return {"agent_id": agent.id, "token": agent.token}


@router.get("/config/{agent_id}")
def get_config(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, object]:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent or not agent.is_active:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent.tenant_id and agent.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: tenant mismatch")

    modules: List[Module] = db.query(Module).all()
    tenant_overrides = {}
    if agent.tenant_id:
        rows = (
            db.query(TenantModule)
            .filter(TenantModule.tenant_id == agent.tenant_id)
            .all()
        )
        tenant_overrides = {row.module_id: row.enabled for row in rows}

    enabled = []
    for module in modules:
        base_enabled = module.is_effectively_enabled
        override = tenant_overrides.get(module.id)
        effective = bool(override) if override is not None else base_enabled
        if effective:
            enabled.append(module.name)

    return {"agent_id": agent.id, "modules": enabled}