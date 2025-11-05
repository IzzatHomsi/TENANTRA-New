from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ServiceSnapshotBase(BaseModel):
    agent_id: int
    name: str
    display_name: Optional[str] = None
    status: str
    start_mode: Optional[str] = None
    run_account: Optional[str] = None
    binary_path: Optional[str] = None
    hash: Optional[str] = None
    collected_at: Optional[datetime] = None


class ServiceSnapshotCreate(ServiceSnapshotBase):
    pass


class ServiceSnapshotRead(ServiceSnapshotBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class TaskSnapshotBase(BaseModel):
    agent_id: int
    name: str
    task_type: str
    schedule: Optional[str] = None
    command: str
    last_run_time: Optional[datetime] = None
    next_run_time: Optional[datetime] = None
    status: Optional[str] = None
    collected_at: Optional[datetime] = None


class TaskSnapshotCreate(TaskSnapshotBase):
    pass


class TaskSnapshotRead(TaskSnapshotBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True
