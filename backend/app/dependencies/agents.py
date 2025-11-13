from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent


def verify_agent_token(
    agent_id: int,
    agent_token: str,
    db: Session,
) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    expected = (agent.token or "").strip()
    if not expected or expected != agent_token.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid agent token")
    if not getattr(agent, "is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent inactive")
    return agent


def get_current_agent(
    agent_id: int,
    agent_token: str = Header(..., alias="X-Agent-Token"),
    db: Session = Depends(get_db),
) -> Agent:
    return verify_agent_token(agent_id, agent_token, db)
