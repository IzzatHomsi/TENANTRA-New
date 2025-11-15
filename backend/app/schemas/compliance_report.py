from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ComplianceReportBase(BaseModel):
    tenant_id: int
    report_type: str
    status: str = "pending"
    file_path: Optional[str] = None
    generated_by: Optional[int] = None


class ComplianceReportCreate(ComplianceReportBase):
    pass


class ComplianceReportUpdate(ComplianceReportBase):
    status: Optional[str] = None
    file_path: Optional[str] = None
    generated_at: Optional[datetime] = None


class ComplianceReportInDB(ComplianceReportBase):
    id: int
    generated_at: datetime

    class Config:
        orm_mode = True
