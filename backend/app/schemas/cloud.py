from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CloudAccountCreate(BaseModel):
    provider: str
    account_identifier: str
    credential_reference: Optional[str] = None
    notes: Optional[str] = None


class CloudAccountRead(CloudAccountCreate):
    id: int
    tenant_id: int
    status: str
    last_synced_at: Optional[datetime]

    class Config:
        orm_mode = True


class CloudAssetCreate(BaseModel):
    account_id: int
    name: str
    asset_type: str
    region: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[str] = None


class CloudAssetRead(CloudAssetCreate):
    id: int
    discovered_at: datetime

    class Config:
        orm_mode = True


class CloudInventoryResponse(BaseModel):
    accounts: List[CloudAccountRead]
    assets: List[CloudAssetRead]
