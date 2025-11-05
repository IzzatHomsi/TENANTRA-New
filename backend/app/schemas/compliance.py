from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class ComplianceFrameworkBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    category: Optional[str] = None


class ComplianceFrameworkCreate(ComplianceFrameworkBase):
    pass


class ComplianceFrameworkRead(ComplianceFrameworkBase):
    id: int

    class Config:
        orm_mode = True


class ComplianceRuleBase(BaseModel):
    control_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    service_area: Optional[str] = None
    framework_ids: List[int] = []
    references: Optional[List[str]] = None


class ComplianceRuleCreate(ComplianceRuleBase):
    pass


class ComplianceRuleRead(ComplianceRuleBase):
    id: int

    class Config:
        orm_mode = True


class ComplianceMatrixResponse(BaseModel):
    frameworks: List[ComplianceFrameworkRead]
    rules: List[ComplianceRuleRead]
