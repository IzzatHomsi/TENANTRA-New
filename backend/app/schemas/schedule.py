from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    module_id: int = Field(..., ge=1)
    cron_expr: str = Field(..., min_length=1, description="Cron expression using minute granularity")
    agent_id: Optional[int] = Field(None, ge=1)
    parameters: Optional[Dict[str, Any]] = Field(None, description="Module execution parameters for this schedule")
    tenant_id: Optional[int] = Field(None, ge=1, description="Override tenant scope (super admins only)")


class ScheduleOut(BaseModel):
    id: int
    tenant_id: int
    module_id: Optional[int]
    agent_id: Optional[int]
    cron_expr: str
    status: str
    enabled: bool
    parameters: Optional[Dict[str, Any]]
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj):  # type: ignore[override]
        return cls(
            id=obj.id,
            tenant_id=obj.tenant_id,
            module_id=getattr(obj, "module_id", None),
            agent_id=getattr(obj, "agent_id", None),
            cron_expr=getattr(obj, "schedule", ""),
            status=obj.status,
            enabled=bool(getattr(obj, "enabled", True)),
            parameters=getattr(obj, "parameters", None),
            last_run_at=getattr(obj, "last_run_at", None),
            next_run_at=getattr(obj, "next_run_at", None),
            created_at=obj.created_at,
            updated_at=getattr(obj, "updated_at", obj.created_at),
        )

    class Config:
        arbitrary_types_allowed = True
