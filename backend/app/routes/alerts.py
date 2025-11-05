from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.alert_rule import AlertRule
from app.models.user import User

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def _resolve_tenant_scope(user: User, tenant_id: Optional[int]) -> int:
    """
    Ensure callers only operate within their tenant. Super admins (tenant_id is None)
    must explicitly pass a tenant_id.
    """
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id required for global administrators")
    return tenant_id


def _serialize(alert: AlertRule) -> Dict[str, object]:
    return {
        "id": alert.id,
        "tenant_id": alert.tenant_id,
        "name": alert.name,
        "condition": alert.condition,
        "threshold": alert.threshold,
        "enabled": alert.enabled,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
    }


@router.get("", response_model=List[Dict[str, object]])
def list_alerts(
    tenant_id: Optional[int] = Query(None, description="Tenant scope (required for global administrators)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> List[Dict[str, object]]:
    resolved_tenant = _resolve_tenant_scope(current_user, tenant_id)
    rows = (
        db.query(AlertRule)
        .filter(AlertRule.tenant_id == resolved_tenant)
        .order_by(AlertRule.id.asc())
        .all()
    )
    return [_serialize(row) for row in rows]


@router.post("", response_model=Dict[str, object], status_code=status.HTTP_201_CREATED)
def create_alert(
    alert: Dict[str, object],
    tenant_id: Optional[int] = Query(None, description="Tenant scope (required for global administrators)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Dict[str, object]:
    resolved_tenant = _resolve_tenant_scope(current_user, tenant_id)
    new_alert = AlertRule(
        tenant_id=resolved_tenant,
        name=str(alert.get("name", "")).strip(),
        condition=str(alert.get("condition", "")).strip(),
        threshold=alert.get("threshold"),
        enabled=bool(alert.get("enabled", True)),
    )
    if not new_alert.name or not new_alert.condition:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'name' and 'condition' are required")
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return _serialize(new_alert)


@router.put("/{alert_id}", response_model=Dict[str, object])
def update_alert(
    alert_id: int,
    data: Dict[str, object],
    tenant_id: Optional[int] = Query(None, description="Tenant scope (required for global administrators)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Dict[str, object]:
    resolved_tenant = _resolve_tenant_scope(current_user, tenant_id)
    alert = (
        db.query(AlertRule)
        .filter(AlertRule.id == alert_id, AlertRule.tenant_id == resolved_tenant)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for key in ("name", "condition", "threshold", "enabled"):
        if key in data:
            if key in {"name", "condition"} and not str(data[key]).strip():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'{key}' cannot be empty")
            setattr(alert, key, data[key])
    db.commit()
    db.refresh(alert)
    return _serialize(alert)


@router.delete("/{alert_id}", response_model=Dict[str, object])
def delete_alert(
    alert_id: int,
    tenant_id: Optional[int] = Query(None, description="Tenant scope (required for global administrators)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Dict[str, object]:
    resolved_tenant = _resolve_tenant_scope(current_user, tenant_id)
    alert = (
        db.query(AlertRule)
        .filter(AlertRule.id == alert_id, AlertRule.tenant_id == resolved_tenant)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"deleted": True, "id": alert_id}
