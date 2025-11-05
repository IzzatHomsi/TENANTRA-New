"""Notification preferences endpoints.

Provide per-tenant and per-user notification preferences that control
enabled channels, event toggles, and digest strategy.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.notification_pref import NotificationPreference
from app.models.user import User
from app.schemas.notification_prefs import (
    NotificationPrefsRead,
    NotificationPrefsUpsert,
)


router = APIRouter(prefix="/notification-prefs", tags=["Notifications"])


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id required")
    return tenant_id


@router.get("", response_model=NotificationPrefsRead)
def get_prefs(
    tenant_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None, description="If provided, return user-specific override if present."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationPrefsRead:
    resolved = _resolve_tenant(current_user, tenant_id)
    row = None
    if user_id is not None:
        row = (
            db.query(NotificationPreference)
            .filter(
                NotificationPreference.tenant_id == resolved,
                NotificationPreference.user_id == user_id,
            )
            .first()
        )
    if row is None:
        row = (
            db.query(NotificationPreference)
            .filter(
                NotificationPreference.tenant_id == resolved,
                NotificationPreference.user_id.is_(None),
            )
            .first()
        )
    if row is None:
        # Return sensible defaults without creating a row
        return NotificationPrefsRead(
            id=0,
            tenant_id=resolved,
            user_id=user_id,
            channels={"email": True, "webhook": False},
            events={
                "scan_failed": True,
                "compliance_violation": True,
                "agent_offline": True,
                "threshold_breach": False,
            },
            digest="immediate",
        )
    return NotificationPrefsRead.from_orm(row)


@router.put("", response_model=NotificationPrefsRead)
def upsert_prefs(
    payload: NotificationPrefsUpsert,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationPrefsRead:
    resolved = _resolve_tenant(current_user, tenant_id)
    # Only allow updating your own user overrides unless admin
    if payload.user_id is not None and current_user.role not in {"admin", "super_admin", "system_admin", "msp_admin"}:
        if payload.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot update other users' preferences")

    row = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.tenant_id == resolved,
            (
                (NotificationPreference.user_id == payload.user_id)
                if payload.user_id is not None
                else NotificationPreference.user_id.is_(None)
            ),
        )
        .first()
    )
    if row is None:
        row = NotificationPreference(
            tenant_id=resolved,
            user_id=payload.user_id,
            channels=dict(payload.channels or {}),
            events=dict(payload.events or {}),
            digest=payload.digest or "immediate",
        )
        db.add(row)
    else:
        row.channels = dict(payload.channels or {})
        row.events = dict(payload.events or {})
        row.digest = payload.digest or row.digest

    db.commit()
    db.refresh(row)
    return NotificationPrefsRead.from_orm(row)

