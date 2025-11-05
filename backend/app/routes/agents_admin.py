"""Admin endpoints to list agents with optional tenant filter."""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.agent import Agent
from app.models.user import User


router = APIRouter(prefix="/admin/agents", tags=["Admin Agents"])


def _serialize(a: Agent) -> Dict[str, object]:
    return {
        "id": a.id,
        "name": a.name,
        "tenant_id": a.tenant_id,
        "is_active": a.is_active,
        "last_seen_at": getattr(a, "last_seen_at", None),
    }


@router.get("", response_model=List[Dict[str, object]])
def list_agents(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> List[Dict[str, object]]:
    q = db.query(Agent)
    if tenant_id is not None:
        q = q.filter(Agent.tenant_id == tenant_id)
    rows = q.order_by(Agent.id.asc()).limit(500).all()
    return [_serialize(r) for r in rows]

