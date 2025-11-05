from __future__ import annotations

from typing import Dict, List, Optional
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.app_setting import AppSetting
from app.models.user import User

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])


def _serialize(setting: AppSetting) -> dict:
    return {"id": setting.id, "tenant_id": setting.tenant_id, "key": setting.key, "value": setting.value}


def _compute_etag(items: List[dict], tenant_key: Optional[str] = None) -> str:
    payload = {"items": items}
    if tenant_key is not None:
        payload["tenant"] = tenant_key
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f'W/"{hashlib.sha256(raw).hexdigest()}"'


def _apply_conditional_headers(
    request: Request,
    response: Response,
    items: List[dict],
    tenant_key: Optional[str] = None,
) -> Optional[Response]:
    etag = _compute_etag(items, tenant_key)
    if request.headers.get("if-none-match") == etag:
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED,
            headers={"ETag": etag, "Cache-Control": "no-cache"},
        )
    response.headers["ETag"] = etag
    response.headers.setdefault("Cache-Control", "no-cache")
    return None


@router.get("", response_model=List[dict])
def list_global_settings(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> List[dict] | Response:
    rows = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None))
        .order_by(AppSetting.key.asc())
        .all()
    )
    payload = [_serialize(row) for row in rows]
    conditional = _apply_conditional_headers(request, response, payload)
    if conditional is not None:
        return conditional  # type: ignore[return-value]
    return payload


@router.put("", response_model=List[dict])
def upsert_global_settings(
    payload: Dict[str, object],
    response: Response,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> List[dict]:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Expected JSON object of key->value pairs")
    out: List[AppSetting] = []
    for key, value in payload.items():
        key_str = (key or "").strip()
        if not key_str:
            continue
        row = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id.is_(None), AppSetting.key == key_str)
            .first()
        )
        if row:
            row.value = value
        else:
            row = AppSetting(tenant_id=None, key=key_str, value=value)
            db.add(row)
        db.commit()
        db.refresh(row)
        out.append(row)
    result = [_serialize(r) for r in out]
    full_payload = [
        _serialize(row)
        for row in db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None))
        .order_by(AppSetting.key.asc())
        .all()
    ]
    if full_payload:
        response.headers["ETag"] = _compute_etag(full_payload)
    response.headers.setdefault("Cache-Control", "no-cache")
    return result


@router.get("/tenant", response_model=List[dict])
def list_tenant_settings(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user),
) -> List[dict] | Response:
    rows = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id == user.tenant_id)
        .order_by(AppSetting.key.asc())
        .all()
    )
    payload = [_serialize(row) for row in rows]
    tenant_key = str(user.tenant_id) if user.tenant_id is not None else "global"
    conditional = _apply_conditional_headers(request, response, payload, tenant_key=tenant_key)
    if conditional is not None:
        return conditional  # type: ignore[return-value]
    return payload


@router.put("/tenant", response_model=List[dict])
def upsert_tenant_settings(
    payload: Dict[str, object],
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user),
) -> List[dict]:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Expected JSON object of key->value pairs")
    out: List[AppSetting] = []
    for key, value in payload.items():
        key_str = (key or "").strip()
        if not key_str:
            continue
        row = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == user.tenant_id, AppSetting.key == key_str)
            .first()
        )
        if row:
            row.value = value
        else:
            row = AppSetting(tenant_id=user.tenant_id, key=key_str, value=value)
            db.add(row)
        db.commit()
        db.refresh(row)
        out.append(row)
    result = [_serialize(r) for r in out]
    tenant_key = str(user.tenant_id) if user.tenant_id is not None else "global"
    full_payload = [
        _serialize(row)
        for row in db.query(AppSetting)
        .filter(AppSetting.tenant_id == user.tenant_id)
        .order_by(AppSetting.key.asc())
        .all()
    ]
    if full_payload:
        response.headers["ETag"] = _compute_etag(full_payload, tenant_key=tenant_key)
    response.headers.setdefault("Cache-Control", "no-cache")
    return result
