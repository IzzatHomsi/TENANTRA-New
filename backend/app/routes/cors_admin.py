from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tenant_cors_origin import TenantCORSOrigin
from app.models.user import User
from app.core.auth import get_current_user

router = APIRouter(prefix="/admin/cors", tags=["Admin CORS"])

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user

def _serialize(row: TenantCORSOrigin) -> dict:
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "origin": row.origin,
        "enabled": row.enabled,
        "is_global": row.is_global,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }

@router.get("", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_origin(
    data: dict,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    tenant_id = data.get("tenant_id")
    origin = (data.get("origin") or "").strip()
    is_global = bool(data.get("is_global") or False)
    if not tenant_id or not origin:
        raise HTTPException(status_code=400, detail="tenant_id and origin are required")
    if db.query(TenantCORSOrigin).filter(TenantCORSOrigin.tenant_id == tenant_id, TenantCORSOrigin.origin == origin).first():
        raise HTTPException(status_code=400, detail="origin already exists for tenant")
    row = TenantCORSOrigin(tenant_id=tenant_id, origin=origin, is_global=is_global, enabled=True)
    db.add(row); db.commit(); db.refresh(row)
    return {"message": "origin added", "origin": _serialize(row)}

@router.patch("/{origin_id}", response_model=dict)
def update_origin(
    origin_id: int,
    data: dict,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    row = db.query(TenantCORSOrigin).filter(TenantCORSOrigin.id == origin_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="origin not found")
    if "enabled" in data:
        row.enabled = bool(data["enabled"])
    if "is_global" in data:
        row.is_global = bool(data["is_global"])
    if "origin" in data and (new := (data["origin"] or "").strip()):
        row.origin = new
    db.commit(); db.refresh(row)
    return {"message": "origin updated", "origin": _serialize(row)}

@router.delete("/{origin_id}", response_model=dict)
def delete_origin(
    origin_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    row = db.query(TenantCORSOrigin).filter(TenantCORSOrigin.id == origin_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="origin not found")
    db.delete(row); db.commit()
    return {"message": "origin deleted", "deleted_id": origin_id}
