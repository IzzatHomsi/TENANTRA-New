from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IOCFeedBase(BaseModel):
    name: str
    source: Optional[str] = None
    feed_type: str = Field("indicator")
    description: Optional[str] = None
    url: Optional[str] = None
    api_key_name: Optional[str] = None
    enabled: bool = True


class IOCFeedCreate(IOCFeedBase):
    pass


class IOCFeedRead(IOCFeedBase):
    id: int
    last_synced_at: Optional[datetime]

    class Config:
        orm_mode = True


class IOCHitBase(BaseModel):
    feed_id: int
    indicator_type: str
    indicator_value: str
    entity_type: str
    entity_identifier: Optional[str] = None
    severity: str = "medium"
    context: Optional[str] = None
    detected_at: Optional[datetime] = None


class IOCHitCreate(IOCHitBase):
    pass


class IOCHitRead(IOCHitBase):
    id: int
    tenant_id: int

    class Config:
        orm_mode = True
