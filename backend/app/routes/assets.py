# backend/app/routes/assets.py
# Read-only listing for assets (Phase 8 visibility support).

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.dependencies.tenancy import tenant_scope_dependency

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("", summary="List assets")
def list_assets(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(tenant_scope_dependency()),
):
    query = (
        db.query(Asset)
        .with_entities(
            Asset.id,
            Asset.tenant_id,
            Asset.name,
            Asset.hostname,
            Asset.ip_address,
            Asset.os,
            Asset.last_seen,
        )
    )

    query = query.filter(Asset.tenant_id == tenant_id)

    rows = query.order_by(Asset.id.asc()).limit(200).all()
    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "name": r.name,
            "hostname": r.hostname,
            "ip_address": r.ip_address,
            "os": r.os,
            "last_seen": r.last_seen,
        }
        for r in rows
    ]
