from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.agent import Agent
from app.models.agent_log import AgentLog
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/agents", tags=["Agent Logs"])


def _ensure_agent_for_tenant(agent_id: int, current_user: User, db: Session) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if agent.tenant_id and current_user.tenant_id not in {None, agent.tenant_id}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: tenant mismatch")
    return agent


def _authenticate_agent(agent_id: int, token: str, db: Session) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    expected = (agent.token or "").strip()
    if not expected or not token or token.strip() != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid agent token")
    if str(getattr(agent, "status", "active")).lower() not in {"active", "online"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent is not active")
    return agent


class LogInput(BaseModel):
    severity: str
    message: str


@router.post("/{agent_id}/logs", response_model=Dict[str, object], status_code=status.HTTP_201_CREATED)
def create_agent_log(
    agent_id: int,
    payload: LogInput,
    db: Session = Depends(get_db),
    agent_token: str = Header(..., alias="X-Agent-Token"),
):
    agent = _authenticate_agent(agent_id, agent_token, db)
    log = AgentLog(
        agent_id=agent_id,
        severity=payload.severity,
        message=payload.message,
        created_at=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"status": "created", "log_id": log.id}


@router.get("/{agent_id}/logs", response_model=List[dict])
def get_agent_logs(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ensure_agent_for_tenant(agent_id, current_user, db)
    logs = (
        db.query(AgentLog)
        .filter(AgentLog.agent_id == agent_id)
        .order_by(AgentLog.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": log.id,
            "severity": log.severity,
            "message": log.message,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
