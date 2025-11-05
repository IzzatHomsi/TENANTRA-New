"""
Visibility API endpoints.

These endpoints provide access to file and network visibility data
captured by agents.  Authenticated users may retrieve visibility
records for agents within their tenant.  The API supports basic
filtering by agent and date range.  Administrative endpoints for
inserting visibility results are not exposed here; results are
inserted by the agent subsystem when scans are executed.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.agent import Agent
from app.models.file_visibility_result import FileVisibilityResult
from app.models.network_visibility_result import NetworkVisibilityResult


router = APIRouter(prefix="/visibility", tags=["Visibility"])


def _validate_agent(agent_id: int, current_user: User, db: Session) -> Agent:
    """Ensure the agent exists and belongs to the current tenant.

    Raises 404 if the agent does not exist or 403 if the tenant does
    not match.  Returns the agent record on success.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent or not agent.is_active:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.tenant_id and agent.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: tenant mismatch")
    return agent


@router.get("/files")
def list_file_visibility(
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    days: Optional[int] = Query(None, ge=1, description="Number of days back to include"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, object]]:
    """Return file visibility results.

    If ``agent_id`` is provided, restrict results to that agent.  If
    ``days`` is provided, only results recorded in the past ``days``
    days are returned.  Results are ordered by ``recorded_at``
    descending.
    """
    query = db.query(FileVisibilityResult)
    if agent_id is not None:
        # Validate agent belongs to tenant
        _validate_agent(agent_id, current_user, db)
        query = query.filter(FileVisibilityResult.agent_id == agent_id)
    else:
        # Only include agents within tenant if not super admin
        if current_user.tenant_id is not None:
            query = query.join(Agent).filter(Agent.tenant_id == current_user.tenant_id)
    if days is not None:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(FileVisibilityResult.recorded_at >= since)
    results = query.order_by(FileVisibilityResult.recorded_at.desc()).all()
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "file_path": r.file_path,
            "share_name": r.share_name,
            "recorded_at": r.recorded_at.isoformat(),
        }
        for r in results
    ]


@router.get("/network")
def list_network_visibility(
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    days: Optional[int] = Query(None, ge=1, description="Number of days back to include"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, object]]:
    """Return network visibility results.

    If ``agent_id`` is provided, restrict results to that agent.  If
    ``days`` is provided, only results recorded in the past ``days``
    days are returned.  Results are ordered by ``recorded_at``
    descending.
    """
    query = db.query(NetworkVisibilityResult)
    if agent_id is not None:
        _validate_agent(agent_id, current_user, db)
        query = query.filter(NetworkVisibilityResult.agent_id == agent_id)
    else:
        if current_user.tenant_id is not None:
            query = query.join(Agent).filter(Agent.tenant_id == current_user.tenant_id)
    if days is not None:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(NetworkVisibilityResult.recorded_at >= since)
    results = query.order_by(NetworkVisibilityResult.recorded_at.desc()).all()
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "port": r.port,
            "service": r.service,
            "status": r.status,
            "recorded_at": r.recorded_at.isoformat(),
        }
        for r in results
    ]