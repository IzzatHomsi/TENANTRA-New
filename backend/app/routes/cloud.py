"""Cloud discovery and connector endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.cloud_account import CloudAccount, CloudAsset
from app.models.user import User
from app.schemas.cloud import (
    CloudAccountCreate,
    CloudAccountRead,
    CloudAssetCreate,
    CloudAssetRead,
    CloudInventoryResponse,
)

router = APIRouter(prefix="/cloud", tags=["Cloud Discovery"])


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id required")
    return tenant_id


@router.get("/accounts", response_model=List[CloudAccountRead])
def list_accounts(
    tenant_id: Optional[int] = Query(None),
    provider: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CloudAccountRead]:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    query = db.query(CloudAccount).filter(CloudAccount.tenant_id == resolved_tenant)
    if provider:
        query = query.filter(CloudAccount.provider == provider)
    accounts = query.order_by(CloudAccount.created_at.desc()).all()
    return [CloudAccountRead.from_orm(account) for account in accounts]


@router.post("/accounts", response_model=CloudAccountRead, status_code=201)
def create_account(
    payload: CloudAccountCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CloudAccountRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    account = CloudAccount(
        tenant_id=resolved_tenant,
        provider=payload.provider,
        account_identifier=payload.account_identifier,
        credential_reference=payload.credential_reference,
        notes=payload.notes,
        status="pending",
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return CloudAccountRead.from_orm(account)


@router.post("/accounts/{account_id}/sync", response_model=CloudAccountRead)
def sync_account(
    account_id: int = Path(...),
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CloudAccountRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    account = (
        db.query(CloudAccount)
        .filter(CloudAccount.id == account_id, CloudAccount.tenant_id == resolved_tenant)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.status = "active"
    account.last_synced_at = datetime.utcnow()
    db.add(account)
    db.commit()
    db.refresh(account)
    return CloudAccountRead.from_orm(account)


@router.get("/assets", response_model=List[CloudAssetRead])
def list_assets(
    tenant_id: Optional[int] = Query(None),
    account_id: Optional[int] = Query(None),
    asset_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CloudAssetRead]:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    query = db.query(CloudAsset).join(CloudAccount).filter(CloudAccount.tenant_id == resolved_tenant)
    if account_id:
        query = query.filter(CloudAsset.account_id == account_id)
    if asset_type:
        query = query.filter(CloudAsset.asset_type == asset_type)
    assets = query.order_by(CloudAsset.discovered_at.desc()).all()
    return [CloudAssetRead.from_orm(asset) for asset in assets]


@router.post("/assets", response_model=CloudAssetRead, status_code=201)
def create_asset(
    payload: CloudAssetCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CloudAssetRead:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    account = (
        db.query(CloudAccount)
        .filter(CloudAccount.id == payload.account_id, CloudAccount.tenant_id == resolved_tenant)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    asset = CloudAsset(
        account_id=payload.account_id,
        name=payload.name,
        asset_type=payload.asset_type,
        region=payload.region,
        status=payload.status,
        metadata=payload.metadata,
        discovered_at=datetime.utcnow(),
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return CloudAssetRead.from_orm(asset)


@router.get("/inventory", response_model=CloudInventoryResponse)
def inventory(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CloudInventoryResponse:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    accounts = db.query(CloudAccount).filter(CloudAccount.tenant_id == resolved_tenant).all()
    assets = (
        db.query(CloudAsset)
        .join(CloudAccount)
        .filter(CloudAccount.tenant_id == resolved_tenant)
        .all()
    )
    return CloudInventoryResponse(
        accounts=[CloudAccountRead.from_orm(account) for account in accounts],
        assets=[CloudAssetRead.from_orm(asset) for asset in assets],
    )
