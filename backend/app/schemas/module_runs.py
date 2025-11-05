from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ModuleRunRequest(BaseModel):
    agent_id: Optional[int] = Field(None, description="Agent initiating the scan")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Runner-specific parameters")


class ModuleRunResponse(BaseModel):
    id: int
    module_id: int
    tenant_id: Optional[int]
    agent_id: Optional[int]
    status: str
    details: Dict[str, Any]
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj):  # type: ignore[override]
        details = obj.details_as_dict() if hasattr(obj, "details_as_dict") else {}
        return cls(
            id=obj.id,
            module_id=obj.module_id,
            tenant_id=getattr(obj, "tenant_id", None),
            agent_id=getattr(obj, "agent_id", None),
            status=obj.status,
            details=details,
            recorded_at=obj.recorded_at,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    class Config:
        arbitrary_types_allowed = True