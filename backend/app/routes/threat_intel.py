"""Threat intelligence feed and IOC hit management."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.ioc_feed import IOCFeed
from app.models.ioc_hit import IOCHit
from app.models.user import User
from app.schemas.threat_intel import IOCFeedCreate, IOCFeedRead, IOCHitCreate, IOCHitRead

router = APIRouter(prefix="/threat-intel", tags=["Threat Intelligence"])


def _require_admin(user: User) -> None:
    if user.role not in {"admin", "super_admin"}:
        raise HTTPException(status_code=403, detail="Administrative role required")


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id required for MSP actions")
    return tenant_id


@router.get("/feeds", response_model=List[IOCFeedRead])
def list_feeds(
    include_disabled: bool = Query(False, description="Return disabled feeds"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[IOCFeedRead]:
    _require_admin(current_user)
    query = db.query(IOCFeed)
    if not include_disabled:
        query = query.filter(IOCFeed.enabled.is_(True))
    feeds = query.order_by(IOCFeed.name.asc()).all()
    return [IOCFeedRead.from_orm(feed) for feed in feeds]


@router.post("/feeds", response_model=IOCFeedRead, status_code=201)
def create_feed(
    payload: IOCFeedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IOCFeedRead:
    _require_admin(current_user)
    existing = db.query(IOCFeed).filter(IOCFeed.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Feed already exists")
    feed = IOCFeed(
        name=payload.name,
        source=payload.source,
        feed_type=payload.feed_type,
        description=payload.description,
        url=payload.url,
        api_key_name=payload.api_key_name,
        enabled=payload.enabled,
    )
    db.add(feed)
    db.commit()
    db.refresh(feed)
    return IOCFeedRead.from_orm(feed)


@router.post("/feeds/{feed_id}/sync", response_model=IOCFeedRead)
def mark_feed_synced(
    feed_id: int = Path(..., description="Feed identifier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IOCFeedRead:
    _require_admin(current_user)
    feed = db.query(IOCFeed).filter(IOCFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    feed.last_synced_at = datetime.utcnow()
    db.add(feed)
    db.commit()
    db.refresh(feed)
    return IOCFeedRead.from_orm(feed)


@router.get("/hits", response_model=List[IOCHitRead])
def list_hits(
    tenant_id: Optional[int] = Query(None, description="Tenant scope (MSP only)"),
    feed_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[IOCHitRead]:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    query = db.query(IOCHit).filter(IOCHit.tenant_id == resolved_tenant)
    if feed_id is not None:
        query = query.filter(IOCHit.feed_id == feed_id)
    if severity:
        query = query.filter(IOCHit.severity == severity)
    hits = query.order_by(IOCHit.detected_at.desc()).limit(limit).all()
    return [IOCHitRead.from_orm(hit) for hit in hits]


@router.post("/hits", response_model=IOCHitRead, status_code=201)
def create_hit(
    payload: IOCHitCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IOCHitRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    feed = db.query(IOCFeed).filter(IOCFeed.id == payload.feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    hit = IOCHit(
        tenant_id=resolved_tenant,
        feed_id=payload.feed_id,
        indicator_type=payload.indicator_type,
        indicator_value=payload.indicator_value,
        entity_type=payload.entity_type,
        entity_identifier=payload.entity_identifier,
        severity=payload.severity,
        context=payload.context,
        detected_at=payload.detected_at or datetime.utcnow(),
    )
    db.add(hit)
    db.commit()
    db.refresh(hit)
    return IOCHitRead.from_orm(hit)
