"""Notification settings endpoints.

Expose simple CRUD for per-tenant notification settings to satisfy
Phase 8 audit presence. Minimal read/create for now.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models.notification_setting import NotificationSetting
from app.models.user import User


router = APIRouter(prefix="/notifications/settings", tags=["Notifications"])


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id required")
    return tenant_id


@router.get("", response_model=List[dict])
def list_settings(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    resolved = _resolve_tenant(current_user, tenant_id)
    rows = (
        db.query(NotificationSetting)
        .filter(NotificationSetting.tenant_id == resolved)
        .order_by(NotificationSetting.id.desc())
        .all()
    )
    out: List[dict] = []
    for r in rows:
        out.append(
            {
                "id": r.id,
                "tenant_id": r.tenant_id,
                "recipient_id": r.recipient_id,
                "title": r.title,
                "message": r.message,
                "status": r.status,
                "severity": r.severity,
                "sent_at": r.sent_at,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
        )
    return out


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_setting(
    payload: dict,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    resolved = _resolve_tenant(current_user, tenant_id)
    required = ["recipient_id", "title", "message", "status"]
    for k in required:
        if k not in payload:
            raise HTTPException(status_code=422, detail=f"Missing field: {k}")
    row = NotificationSetting(
        recipient_id=int(payload["recipient_id"]),
        tenant_id=resolved,
        title=str(payload["title"]),
        message=str(payload["message"]),
        status=str(payload["status"]),
        severity=str(payload.get("severity") or ""),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "recipient_id": row.recipient_id,
        "title": row.title,
        "message": row.message,
        "status": row.status,
        "severity": row.severity,
        "sent_at": row.sent_at,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }

