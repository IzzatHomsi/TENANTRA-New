from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TenantRetentionPolicyRead(BaseModel):
    tenant_id: int
    retention_days: int
    archive_storage: Optional[str]
    export_formats: List[str]

    class Config:
        orm_mode = True


class TenantRetentionPolicyUpdate(BaseModel):
    retention_days: int = Field(..., ge=30, le=1825)
    archive_storage: Optional[str] = None
    export_formats: List[str] = Field(default_factory=lambda: ["csv", "json", "pdf", "zip"])


class DataExportJobRead(BaseModel):
    id: int
    tenant_id: int
    export_type: str
    status: str
    formats: List[str]
    storage_uri: Optional[str]
    requested_at: datetime
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True


class DataExportJobCreate(BaseModel):
    export_type: str
    formats: List[str]
