from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProcessObservation(BaseModel):
    """Single process entry reported by an endpoint."""

    pid: int = Field(..., description="Operating system process identifier")
    process_name: str = Field(..., description="Process executable name")
    executable_path: Optional[str] = Field(None, description="Full path to executable")
    username: Optional[str] = Field(None, description="Account that owns the process")
    hash: Optional[str] = Field(None, description="File hash (SHA256 recommended)")
    command_line: Optional[str] = Field(None, description="Original command line")
    collected_at: Optional[datetime] = Field(None, description="Timestamp when the agent collected the process")


class ProcessReportRequest(BaseModel):
    agent_id: int = Field(..., description="Agent identifier sending the report")
    processes: List[ProcessObservation] = Field(..., description="Complete process inventory for the agent")
    full_sync: bool = Field(True, description="True when the payload represents the full running process list")


class ProcessSnapshotRead(BaseModel):
    id: int
    agent_id: int
    tenant_id: int
    report_id: str
    process_name: str
    pid: int
    executable_path: Optional[str]
    username: Optional[str]
    hash: Optional[str]
    command_line: Optional[str]
    collected_at: datetime

    class Config:
        from_attributes = True


class ProcessBaselineEntry(BaseModel):
    process_name: str = Field(..., description="Executable name expected on the host")
    executable_path: Optional[str] = Field(None, description="Expected file path")
    expected_hash: Optional[str] = Field(None, description="Expected file hash")
    expected_user: Optional[str] = Field(None, description="Expected owner account")
    is_critical: bool = Field(False, description="Marks process as critical for compliance")
    notes: Optional[str] = Field(None, description="Optional operator notes")


class ProcessBaselineRequest(BaseModel):
    agent_id: Optional[int] = Field(None, description="Agent the baseline applies to; None for tenant-wide")
    processes: List[ProcessBaselineEntry] = Field(default_factory=list)


class ProcessBaselineRead(ProcessBaselineEntry):
    id: int
    tenant_id: int
    agent_id: Optional[int]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProcessDriftRecord(BaseModel):
    change_type: str
    process_name: str
    pid: Optional[int]
    executable_path: Optional[str]
    severity: str
    detected_at: datetime
    details: Optional[str]
    old_value: Optional[dict]
    new_value: Optional[dict]


class ProcessDriftSummary(BaseModel):
    report_id: Optional[str]
    baseline_applied: bool
    events: List[ProcessDriftRecord] = Field(default_factory=list)


class ProcessReportResponse(BaseModel):
    ingested: int
    report_id: str
    drift: ProcessDriftSummary


class ProcessBaselineResponse(BaseModel):
    agent_id: Optional[int]
    entries: List[ProcessBaselineRead]


class ProcessDriftListResponse(BaseModel):
    events: List[ProcessDriftRecord]
