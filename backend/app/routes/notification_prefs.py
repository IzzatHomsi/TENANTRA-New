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
from app.dependencies.tenancy import tenant_scope_dependency


router = APIRouter(tags=["Notifications"])


def _fetch_prefs(
    user_id: Optional[int] = Query(None, description="If provided, return user-specific override if present."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    resolved_tenant: int = Depends(tenant_scope_dependency()),
) -> NotificationPrefsRead:
    row = None
    if user_id is not None:
        row = (
            db.query(NotificationPreference)
            .filter(
                NotificationPreference.tenant_id == resolved_tenant,
                NotificationPreference.user_id == user_id,
            )
            .first()
        )
    if row is None:
        row = (
            db.query(NotificationPreference)
            .filter(
                NotificationPreference.tenant_id == resolved_tenant,
                NotificationPreference.user_id.is_(None),
            )
            .first()
        )
    if row is None:
        # Return sensible defaults without creating a row
        return NotificationPrefsRead(
            id=0,
            tenant_id=resolved_tenant,
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


def _upsert_prefs(
    payload: NotificationPrefsUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    resolved_tenant: int = Depends(tenant_scope_dependency()),
) -> NotificationPrefsRead:
    # Only allow updating your own user overrides unless admin
    if payload.user_id is not None and current_user.role not in {"admin", "super_admin", "system_admin", "msp_admin"}:
        if payload.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot update other users' preferences")

    row = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.tenant_id == resolved_tenant,
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
            tenant_id=resolved_tenant,
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


@router.get("/notification-prefs", response_model=NotificationPrefsRead)
def get_prefs(
    user_id: Optional[int] = Query(None, description="If provided, return user-specific override if present."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    resolved_tenant: int = Depends(tenant_scope_dependency()),
) -> NotificationPrefsRead:
    return _fetch_prefs(user_id, db, current_user, resolved_tenant)


@router.put("/notification-prefs", response_model=NotificationPrefsRead)
def upsert_prefs(
    payload: NotificationPrefsUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    resolved_tenant: int = Depends(tenant_scope_dependency()),
) -> NotificationPrefsRead:
    return _upsert_prefs(payload, db, current_user, resolved_tenant)


@router.get("/notifications/settings", response_model=NotificationPrefsRead)
def get_notification_settings(
    user_id: Optional[int] = Query(None, description="If provided, return user-specific override if present."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    resolved_tenant: int = Depends(tenant_scope_dependency()),
) -> NotificationPrefsRead:
    return _fetch_prefs(user_id, db, current_user, resolved_tenant)


@router.put("/notifications/settings", response_model=NotificationPrefsRead)
def update_notification_settings(
    payload: NotificationPrefsUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    resolved_tenant: int = Depends(tenant_scope_dependency()),
) -> NotificationPrefsRead:
    return _upsert_prefs(payload, db, current_user, resolved_tenant)
