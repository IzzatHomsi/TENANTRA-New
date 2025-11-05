from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.session import get_db
from app.models.module_agent_mapping import ModuleAgentMapping

router = APIRouter(prefix="/modules", tags=["Module Mapping"])

class MappingEntry(BaseModel):
    module_id: int
    agent_id: int
    enabled: bool

@router.get("/mapping", response_model=List[MappingEntry])
def get_mappings(db: Session = Depends(get_db)):
    return db.query(ModuleAgentMapping).all()

@router.put("/mapping")
def update_mappings(payload: List[MappingEntry], db: Session = Depends(get_db)):
    for entry in payload:
        existing = (
            db.query(ModuleAgentMapping)
            .filter_by(module_id=entry.module_id, agent_id=entry.agent_id)
            .first()
        )
        if existing:
            existing.enabled = entry.enabled
        else:
            new_entry = ModuleAgentMapping(
                module_id=entry.module_id,
                agent_id=entry.agent_id,
                enabled=entry.enabled,
            )
            db.add(new_entry)
    db.commit()
    return {"updated": len(payload)}
