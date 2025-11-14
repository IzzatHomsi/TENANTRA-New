"""Agent API endpoints."""

import secrets
from typing import Dict, List, Optional
from datetime import datetime
import json

from fastapi import APIRouter, Body, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, root_validator
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.dependencies.agents import verify_agent_token
from app.models.agent import Agent
from app.models.module import Module
from app.models.module_agent_mapping import ModuleAgentMapping
from app.models.scan_module_result import ScanModuleResult
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


class AgentResultSubmission(BaseModel):
    agent_id: int
    module_id: Optional[int] = None
    module_name: Optional[str] = None
    status: str
    details: Optional[Dict[str, object]] = None

    @root_validator(skip_on_failure=True)
    def _ensure_module_reference(cls, values):
        if not values.get("module_id") and not values.get("module_name"):
            raise ValueError("module_id or module_name is required")
        return values


@router.post("/enroll")
def enroll_agent(
    name: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Dict[str, object]:
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
    tenant_overrides: Dict[int, bool] = {}
    if agent.tenant_id:
        rows = (
            db.query(TenantModule)
            .filter(TenantModule.tenant_id == agent.tenant_id)
            .all()
        )
        tenant_overrides = {row.module_id: bool(row.enabled) for row in rows}

    agent_overrides = {
        row.module_id: bool(row.enabled)
        for row in db.query(ModuleAgentMapping).filter(ModuleAgentMapping.agent_id == agent.id).all()
    }

    enabled = []
    for module in modules:
        base_enabled = module.is_effectively_enabled
        if module.id in agent_overrides:
            effective = agent_overrides[module.id]
        elif module.id in tenant_overrides:
            effective = tenant_overrides[module.id]
        else:
            effective = base_enabled
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


@router.post("/results", status_code=status.HTTP_201_CREATED)
def submit_agent_result(
    payload: AgentResultSubmission,
    agent_token: str = Header(..., alias="X-Agent-Token"),
    db: Session = Depends(get_db),
) -> Dict[str, object]:
    agent = verify_agent_token(payload.agent_id, agent_token, db)
    module = None
    if payload.module_id:
        module = db.query(Module).filter(Module.id == payload.module_id).first()
    if module is None and payload.module_name:
        module = db.query(Module).filter(Module.name == payload.module_name).first()
    if module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    record = ScanModuleResult(
        module_id=module.id,
        agent_id=agent.id,
        tenant_id=agent.tenant_id,
        status=payload.status,
        details=json.dumps(payload.details or {}),
        recorded_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "status": record.status}
