"""Agent API endpoints."""

import secrets
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.dependencies.agents import verify_agent_token
from app.models.agent import Agent
from app.models.module import Module
from app.models.tenant_module import TenantModule
from app.models.user import User
from app.services import agent_enrollment

router = APIRouter(prefix="/agents", tags=["Agents"])

class EnrollmentTokenRequest(BaseModel):
    label: Optional[str] = None
    expires_in_minutes: Optional[int] = Field(None, ge=5, le=1440)


class SelfEnrollRequest(BaseModel):
    token: str
    name: str = Field(..., min_length=1)


@router.post("/enroll")
def enroll_agent(
    name: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Dict[str, str]:
    if current_user.tenant_id is None:
        raise HTTPException(status_code=400, detail="Admin must belong to a tenant")
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Agent name is required")
    token = secrets.token_hex(16)
    agent = Agent(name=name.strip(), token=token, tenant_id=current_user.tenant_id)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return {"agent_id": agent.id, "token": agent.token}


@router.post("/enrollment-tokens", status_code=201)
def create_enrollment_token(
    payload: EnrollmentTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Dict[str, object]:
    if current_user.tenant_id is None:
        raise HTTPException(status_code=400, detail="Admin must belong to a tenant")
    ttl = payload.expires_in_minutes or agent_enrollment.ENROLL_TOKEN_TTL_MINUTES
    raw_token = agent_enrollment.create_enrollment_token(
        db,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        label=payload.label,
        ttl_minutes=ttl,
    )
    return {"token": raw_token, "expires_in_minutes": ttl}


@router.get("/config/{agent_id}")
def get_config(
    agent_id: int,
    agent_token: str = Header(..., alias="X-Agent-Token"),
    db: Session = Depends(get_db),
) -> Dict[str, object]:
    agent = verify_agent_token(agent_id, agent_token, db)

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


@router.post("/enroll/self", status_code=201)
def self_enroll_agent(
    payload: SelfEnrollRequest,
    db: Session = Depends(get_db),
) -> Dict[str, object]:
    try:
        token_record = agent_enrollment.consume_enrollment_token(db, payload.token)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired enrollment token.")
    agent, agent_token = agent_enrollment.create_agent_with_token(
        db,
        tenant_id=token_record.tenant_id,
        name=payload.name.strip(),
    )
    return {"agent_id": agent.id, "token": agent_token}
