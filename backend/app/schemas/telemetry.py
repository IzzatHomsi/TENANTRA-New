from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, validator


class WebVitalPayload(BaseModel):
    name: str = Field(..., description="Metric name (LCP, INP, CLS, etc.)")
    id: str = Field(..., description="Unique identifier for the metric instance")
    value: float = Field(..., description="Measured value")
    rating: Optional[str] = Field(None, description="Performance rating provided by web-vitals")
    navigationType: Optional[str] = Field(None, alias="navigationType")
    timestamp: Optional[int] = Field(None, description="Client timestamp (epoch ms)")
    tenant: Optional[str] = Field(None, description="Tenant identifier if available")
    userId: Optional[str] = Field(None, description="User identifier if available")
    url: Optional[str] = Field(None, description="Page URL when the metric was collected")
    extra: Optional[dict] = Field(None, description="Additional structured data")

    @validator("name")
    def _normalize_name(cls, value: str) -> str:
        v = (value or "").strip().upper()
        if not v:
            raise ValueError("name is required")
        return v

    class Config:
        allow_population_by_field_name = True
