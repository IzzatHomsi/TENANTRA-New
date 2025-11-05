from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ScanJobCreate(BaseModel):
    name: str
    description: Optional[str] = None
    scan_type: str
    priority: str = "normal"
    schedule: Optional[str] = None


class ScanJobRead(ScanJobCreate):
    id: int
    tenant_id: int
    status: str
    created_by: Optional[int]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True
        from_attributes = True


class ScanResultCreate(BaseModel):
    agent_id: Optional[int]
    asset_id: Optional[int]
    status: str = "queued"
    details: Optional[str] = None


class ScanResultRead(ScanResultCreate):
    id: int
    job_id: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True
        from_attributes = True


class ScanJobWithResults(BaseModel):
    job: ScanJobRead
    results: List[ScanResultRead]
