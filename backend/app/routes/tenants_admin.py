"""Admin endpoints for basic tenant management (list/create)."""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User


router = APIRouter(prefix="/admin/tenants", tags=["Admin Tenants"])


def _serialize(t: Tenant) -> Dict[str, object]:
    return {
        "id": t.id,
        "name": t.name,
        "slug": t.slug,
        "is_active": t.is_active,
        "storage_quota_gb": t.storage_quota_gb,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


@router.get("", response_model=List[Dict[str, object]])
def list_tenants(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> List[Dict[str, object]]:
    rows = db.query(Tenant).order_by(Tenant.id.asc()).limit(500).all()
    return [_serialize(r) for r in rows]


@router.post("", response_model=Dict[str, object], status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: Dict[str, object],
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> Dict[str, object]:
    name = (payload.get("name") or "").strip()
    slug = (payload.get("slug") or "").strip()
    if not name or not slug:
        raise HTTPException(status_code=400, detail="'name' and 'slug' are required")
    existing = db.query(Tenant).filter((Tenant.name == name) | (Tenant.slug == slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tenant with same name or slug already exists")
    tenant = Tenant(name=name, slug=slug, is_active=bool(payload.get("is_active", True)))
    quota = payload.get("storage_quota_gb")
    try:
        if quota is not None:
            tenant.storage_quota_gb = int(quota)
    except Exception:
        raise HTTPException(status_code=400, detail="storage_quota_gb must be an integer")
    db.add(tenant)
    db.commit(); db.refresh(tenant)
    return _serialize(tenant)

