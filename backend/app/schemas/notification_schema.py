from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class NotificationCreate(BaseModel):
    title: str
    message: str
    recipient_email: EmailStr
    severity: Optional[str] = None


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    recipient_email: EmailStr
    status: str
    severity: Optional[str] = None
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True