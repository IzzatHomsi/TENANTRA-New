from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationLogCreate(BaseModel):
    notification_id: Optional[int] = None
    channel: str
    recipient: str
    subject: Optional[str] = None
    body: Optional[str] = None
    status: str = "sent"
    error: Optional[str] = None


class NotificationLogRead(NotificationLogCreate):
    id: int
    tenant_id: int
    sent_at: datetime

    class Config:
        orm_mode = True
