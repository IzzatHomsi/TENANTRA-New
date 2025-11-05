"""Notification history endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.notification import Notification
from app.models.notification_log import NotificationLog
from app.models.user import User
from app.schemas.notification_history import NotificationLogCreate, NotificationLogRead

router = APIRouter(prefix="/notification-history", tags=["Notifications"])


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id required")
    return tenant_id


@router.get("", response_model=List[NotificationLogRead])
def list_history(
    tenant_id: Optional[int] = Query(None),
    channel: Optional[str] = Query(None),
    recipient: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[NotificationLogRead]:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    query = db.query(NotificationLog).filter(NotificationLog.tenant_id == resolved_tenant)
    if channel:
        query = query.filter(NotificationLog.channel == channel)
    if recipient:
        query = query.filter(NotificationLog.recipient == recipient)
    history = query.order_by(NotificationLog.sent_at.desc()).limit(limit).all()
    return [NotificationLogRead.from_orm(record) for record in history]


@router.post("", response_model=NotificationLogRead, status_code=201)
def create_history(
    payload: NotificationLogCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationLogRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    if payload.notification_id:
        notification = db.query(Notification).filter(Notification.id == payload.notification_id).first()
        if not notification or notification.tenant_id != resolved_tenant:
            raise HTTPException(status_code=400, detail="Notification scope invalid")
    record = NotificationLog(
        tenant_id=resolved_tenant,
        notification_id=payload.notification_id,
        channel=payload.channel,
        recipient=payload.recipient,
        subject=payload.subject,
        body=payload.body,
        status=payload.status,
        sent_at=datetime.utcnow(),
        error=payload.error,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return NotificationLogRead.from_orm(record)
