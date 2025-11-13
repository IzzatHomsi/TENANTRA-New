from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_enrollment_token import AgentEnrollmentToken

ENROLL_TOKEN_TTL_MINUTES = int(os.getenv("TENANTRA_AGENT_ENROLL_TTL", "15"))


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_enrollment_token(
    db: Session,
    *,
    tenant_id: int,
    created_by: int,
    label: str | None = None,
    ttl_minutes: int = ENROLL_TOKEN_TTL_MINUTES,
) -> str:
    raw_token = secrets.token_urlsafe(32)
    token = AgentEnrollmentToken(
        tenant_id=tenant_id,
        token_hash=_hash_token(raw_token),
        label=label,
        created_by=created_by,
        expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
    )
    db.add(token)
    db.commit()
    return raw_token


def consume_enrollment_token(db: Session, raw_token: str) -> AgentEnrollmentToken:
    token_hash = _hash_token(raw_token)
    token = (
        db.query(AgentEnrollmentToken)
        .filter(
            AgentEnrollmentToken.token_hash == token_hash,
            AgentEnrollmentToken.used_at.is_(None),
            AgentEnrollmentToken.expires_at >= datetime.utcnow(),
        )
        .first()
    )
    if not token:
        raise ValueError("Invalid or expired enrollment token.")
    token.used_at = datetime.utcnow()
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def create_agent_with_token(
    db: Session,
    *,
    tenant_id: int,
    name: str,
) -> tuple[Agent, str]:
    agent_token = secrets.token_hex(16)
    agent = Agent(
        tenant_id=tenant_id,
        name=name,
        token=agent_token,
        status="active",
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent, agent_token
