from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DataExportJobBase(BaseModel):
    tenant_id: int
    requested_by: Optional[int] = None
    export_type: str
    status: str = "pending"
    formats: str
    storage_uri: Optional[str] = None


class DataExportJobCreate(DataExportJobBase):
    pass


class DataExportJobUpdate(DataExportJobBase):
    status: Optional[str] = None
    storage_uri: Optional[str] = None
    completed_at: Optional[datetime] = None


class DataExportJobInDB(DataExportJobBase):
    id: int
    requested_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True
