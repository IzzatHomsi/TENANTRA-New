from __future__ import annotations

from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class NotificationPrefsBase(BaseModel):
    channels: Dict[str, bool] = Field(default_factory=dict)
    events: Dict[str, bool] = Field(default_factory=dict)
    digest: str = Field(default="immediate")


class NotificationPrefsRead(NotificationPrefsBase):
    id: int
    tenant_id: int
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationPrefsUpsert(NotificationPrefsBase):
    # Optional user_id to set explicit user override; omit/null to upsert tenant default
    user_id: Optional[int] = None
