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
            module_id=obj.module_id,
            agent_id=obj.agent_id,
            cron_expr=obj.cron_expr,
            status=obj.status,
            enabled=bool(obj.enabled),
            parameters=getattr(obj, "parameters", None),
            last_run_at=obj.last_run_at,
            next_run_at=obj.next_run_at,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    class Config:
        arbitrary_types_allowed = True
