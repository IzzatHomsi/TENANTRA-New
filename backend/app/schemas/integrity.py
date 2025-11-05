from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class RegistrySnapshotBase(BaseModel):
    agent_id: int = Field(..., description="Agent identifier")
    hive: str = Field(..., description="Registry hive name")
    key_path: str = Field(..., description="Registry key path")
    value_name: Optional[str] = Field(None, description="Registry value name")
    value_data: Optional[str] = Field(None, description="Registry value data")
    value_type: Optional[str] = Field(None, description="Registry value type")
    checksum: Optional[str] = Field(None, description="Checksum of the entry")
    collected_at: Optional[datetime] = Field(None, description="Collection timestamp")


class RegistrySnapshotCreate(RegistrySnapshotBase):
    pass


class RegistrySnapshotRead(RegistrySnapshotBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class BootConfigBase(BaseModel):
    agent_id: int
    platform: str
    config_path: str
    content: str
    checksum: str
    collected_at: Optional[datetime] = None


class BootConfigCreate(BootConfigBase):
    pass


class BootConfigRead(BootConfigBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class IntegrityEventBase(BaseModel):
    agent_id: Optional[int] = None
    event_type: str
    severity: str = Field("medium")
    title: str
    description: Optional[str] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    metadata: Optional[str] = None
    detected_at: Optional[datetime] = None


class IntegrityEventCreate(IntegrityEventBase):
    pass


class IntegrityEventRead(IntegrityEventBase):
    id: int
    tenant_id: int
    resolved_at: Optional[datetime]
    # Map DB attribute 'metadata_json' to API field 'metadata'
    metadata: Optional[str] = Field(default=None, validation_alias='metadata_json', serialization_alias='metadata')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RegistryDriftResponse(BaseModel):
    new_entries: List[RegistrySnapshotRead]
    modified_entries: List[RegistrySnapshotRead]
    removed_entries: List[RegistrySnapshotRead]
