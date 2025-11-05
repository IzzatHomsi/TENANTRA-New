"""Notification management endpoints."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification_schema import NotificationCreate, NotificationOut
from app.utils.audit import log_audit_event
from app.utils.email import send_email
from app.observability.metrics import record_notification_delivery

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> List[Notification]:
    rows = (
        db.query(Notification)
        .filter(Notification.tenant_id == current_user.tenant_id)
        .order_by(Notification.id.desc())
        .all()
    )
    return rows


@router.post("", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Notification:
    email_value = payload.recipient_email.strip()
    recipient = (
        db.query(User)
        .filter(func.lower(User.email) == email_value.lower())
        .first()
    )
    if recipient and recipient.tenant_id not in {None, current_user.tenant_id}:
        raise HTTPException(status_code=403, detail="Recipient belongs to a different tenant")

    tenant_id = current_user.tenant_id or (recipient.tenant_id if recipient else None)
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="Tenant context required to create notification")

    note = Notification(
        tenant_id=tenant_id,
        recipient_id=recipient.id if recipient else None,
        recipient_email=email_value,
        title=payload.title,
        message=payload.message,
        severity=payload.severity,
        status="queued",
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    log_audit_event(
        db,
        user_id=current_user.id,
        action="notification.create",
        result="success",
        ip=None,
    )
    return note


@router.post("/send/{notification_id}", response_model=NotificationOut)
def send_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Notification:
    note = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    ok = send_email(note.recipient_email, note.title, note.message, raise_on_error=False)
    record_notification_delivery("email", ok)
    note.status = "sent" if ok else "failed"
    note.sent_at = datetime.utcnow() if ok else None
    db.commit()
    db.refresh(note)
    log_audit_event(
        db,
        user_id=current_user.id,
        action="notification.send",
        result="success" if ok else "failed",
        ip=None,
    )
    return note


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> dict:
    note = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(note)
    db.commit()
    log_audit_event(
        db,
        user_id=current_user.id,
        action="notification.delete",
        result="success",
        ip=None,
    )
    return {"message": "Notification deleted", "id": notification_id}
