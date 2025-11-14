from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.module_agent_mapping import ModuleAgentMapping
from app.models.agent import Agent
from app.models.user import User
from app.core.auth import get_current_user
from app.utils.rbac import role_required

router = APIRouter(prefix="/modules", tags=["Module Mapping"])

class MappingEntry(BaseModel):
    module_id: int
    agent_id: int
    enabled: bool


@router.get(
    "/mapping",
    response_model=List[MappingEntry],
    dependencies=[Depends(role_required("admin", "super_admin"))],
)
def get_mappings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MappingEntry]:
    query = db.query(ModuleAgentMapping)
    if current_user.tenant_id:
        query = query.join(Agent).filter(Agent.tenant_id == current_user.tenant_id)
    rows = query.all()
    return [MappingEntry(module_id=row.module_id, agent_id=row.agent_id, enabled=bool(row.enabled)) for row in rows]


@router.put(
    "/mapping",
    dependencies=[Depends(role_required("admin", "super_admin"))],
)
def update_mappings(
    payload: List[MappingEntry],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload:
        return {"updated": 0}
    for entry in payload:
        agent = db.query(Agent).filter(Agent.id == entry.agent_id).first()
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent {entry.agent_id} not found")
        if current_user.tenant_id and agent.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent belongs to a different tenant")
        existing = (
            db.query(ModuleAgentMapping)
            .filter_by(module_id=entry.module_id, agent_id=entry.agent_id)
            .first()
        )
        if existing:
            existing.enabled = bool(entry.enabled)
        else:
            db.add(
                ModuleAgentMapping(
                    module_id=entry.module_id,
                    agent_id=entry.agent_id,
                    enabled=bool(entry.enabled),
                )
            )
    db.commit()
    return {"updated": len(payload)}


@router.delete(
    "/mapping/{agent_id}/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_required("admin", "super_admin"))],
)
def delete_mapping(
    agent_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if current_user.tenant_id and agent.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent belongs to a different tenant")
    mapping = (
        db.query(ModuleAgentMapping)
        .filter_by(agent_id=agent_id, module_id=module_id)
        .first()
    )
    if mapping:
        db.delete(mapping)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
