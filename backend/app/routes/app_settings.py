from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from urllib.parse import urlparse, urlunparse

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationError,
    confloat,
    conint,
    constr,
    root_validator,
    validator,
)

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.app_setting import AppSetting
from app.models.user import User
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])


_UNSET = object()


def _serialize(setting: AppSetting, *, value: Any = _UNSET) -> dict:
    resolved_value = setting.value if value is _UNSET else value
    return {
        "id": setting.id,
        "tenant_id": setting.tenant_id,
        "key": setting.key,
        "value": resolved_value,
    }


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


class _PortTarget(BaseModel):
    host: constr(strip_whitespace=True, min_length=1, max_length=255)
    ports: List[conint(ge=1, le=65535)]
    protocol: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=5) = "tcp"
    tags: List[constr(strip_whitespace=True, min_length=1, max_length=40)] = Field(default_factory=list)

    class Config:
        extra = "forbid"

    @validator("ports")
    def ensure_unique_ports(cls, ports: List[int]) -> List[int]:
        seen = set()
        ordered: List[int] = []
        for value in ports:
            if value in seen:
                raise ValueError("Duplicate port values are not allowed")
            seen.add(value)
            ordered.append(value)
        return ordered


class _DHCPScope(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=120)
    total_leases: conint(ge=0)
    active_leases: conint(ge=0)
    reserved_leases: conint(ge=0) = 0
    dhcp_server: Optional[constr(strip_whitespace=True, min_length=1, max_length=120)] = None
    site: Optional[constr(strip_whitespace=True, min_length=1, max_length=120)] = None
    vlan: Optional[constr(strip_whitespace=True, min_length=1, max_length=40)] = None
    tags: List[constr(strip_whitespace=True, min_length=1, max_length=40)] = Field(default_factory=list)

    class Config:
        extra = "forbid"

    @root_validator
    def validate_capacity(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        total = values.get("total_leases") or 0
        active = values.get("active_leases") or 0
        reserved = values.get("reserved_leases") or 0
        if active > total:
            raise ValueError("active_leases cannot exceed total_leases")
        if reserved > total:
            raise ValueError("reserved_leases cannot exceed total_leases")
        return values


class _DHCPSource(BaseModel):
    type: constr(strip_whitespace=True, min_length=2, max_length=32)
    endpoint: Optional[constr(strip_whitespace=True, min_length=1, max_length=500)] = None
    username: Optional[constr(strip_whitespace=True, min_length=1, max_length=120)] = None
    password: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    api_key: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    verify_tls: bool = True
    timeout_seconds: confloat(gt=0, le=600) = 10.0

    class Config:
        extra = "forbid"

    @validator("endpoint")
    def validate_endpoint(cls, value: Optional[str]) -> Optional[str]:
        if value in (None, ""):
            return None
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Endpoint must include scheme and host")
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "", "", "", ""))

    @validator("type")
    def normalize_type(cls, value: str) -> str:
        return value.lower()


class _FeatureFlagMap(BaseModel):
    __root__: Dict[str, bool]

    @validator("__root__")
    def ensure_boolean_map(cls, value: Dict[str, Any]) -> Dict[str, bool]:
        if not isinstance(value, dict):
            raise ValueError("features must be a JSON object of feature->enabled flags")
        normalized: Dict[str, bool] = {}
        for key, raw in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Feature keys must be non-empty strings")
            normalized[key.strip()] = bool(raw)
        return normalized


class _AppSettingsPayload(BaseModel):
    grafana_url: Optional[str] = Field(None, alias="grafana.url")
    grafana_dashboard_uid: Optional[constr(strip_whitespace=True, min_length=2, max_length=120, regex=r"^[A-Za-z0-9_\-]+$")] = Field(
        None, alias="grafana.dashboard_uid"
    )
    grafana_datasource_uid: Optional[constr(strip_whitespace=True, min_length=2, max_length=120, regex=r"^[A-Za-z0-9_\-]+$")] = Field(
        None, alias="grafana.datasource_uid"
    )
    theme_color_primary: Optional[constr(strip_whitespace=True, regex=r"^#[0-9A-Fa-f]{6}$")] = Field(
        None, alias="theme.colors.primary"
    )
    email_redirect_enabled: Optional[bool] = Field(None, alias="email.redirect.enabled")
    email_redirect_to: Optional[EmailStr] = Field(None, alias="email.redirect.to")
    networking_plan_targets: Optional[List[_PortTarget]] = Field(None, alias="networking.plan.targets")
    networking_dhcp_scopes: Optional[List[_DHCPScope]] = Field(None, alias="networking.dhcp.scopes")
    networking_dhcp_source: Optional[_DHCPSource] = Field(None, alias="networking.dhcp.source")
    feature_flags: Optional[_FeatureFlagMap] = Field(None, alias="features")
    worker_enabled: Optional[bool] = Field(None, alias="worker.enabled")
    tenant_mode: Optional[constr(strip_whitespace=True, to_lower=True)] = Field(None, alias="tenant.mode")
    onboarding_done: Optional[bool] = Field(None, alias="onboarding.done")

    class Config:
        allow_population_by_field_name = True
        extra = "forbid"

    @validator("grafana_url", pre=True)
    def _normalize_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
        if not value:
            return None
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Grafana URL must include scheme and host (e.g., https://grafana.example.com)")
        if parsed.scheme not in {"https", "http"}:
            raise ValueError("Grafana URL must use http or https")
        insecure_hosts = {"grafana", "grafana.local", "localhost", "127.0.0.1"}
        if parsed.scheme != "https" and parsed.hostname not in insecure_hosts:
            raise ValueError("Grafana URL must use https outside of local development")
        normalized_path = parsed.path.rstrip("/") or ""
        normalized = urlunparse((parsed.scheme, parsed.netloc, normalized_path, "", "", ""))
        return normalized

    @validator("grafana_dashboard_uid", "grafana_datasource_uid", pre=True)
    def _strip_identifiers(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
        if not value:
            return None
        return value

    @validator("theme_color_primary", pre=True)
    def _normalize_color(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not value.startswith("#"):
            value = f"#{value}"
        return value.lower()

    @validator("email_redirect_to", pre=True)
    def _normalize_email(cls, value: Optional[str]) -> Optional[str]:
        if value in (None, "", False):
            return None
        return value

    @validator("email_redirect_to", always=True)
    def _validate_email_redirect(cls, value: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        enabled = values.get("email_redirect_enabled")
        if enabled and not value:
            raise ValueError("Provide a redirect address when email redirect is enabled")
        if not enabled:
        return None
    return value

    @validator("tenant_mode", pre=True)
    def _normalize_tenant_mode(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().lower()
        if value not in {"single", "multi"}:
            raise ValueError("tenant.mode must be 'single' or 'multi'")
        return value

    @validator("networking_plan_targets", "networking_dhcp_scopes", pre=True)
    def _allow_empty_iterable(cls, value: Optional[Iterable[Any]]) -> Optional[Iterable[Any]]:
        if value is None:
            return None
        if isinstance(value, list) and len(value) == 0:
            return []
        return value

    def to_updates(self) -> Dict[str, Any]:
        raw = self.dict(by_alias=True, exclude_unset=True)
        normalized: Dict[str, Any] = {}
        for key, value in raw.items():
            if isinstance(value, list):
                normalized[key] = [
                    item.dict(exclude_none=True)
                    if isinstance(item, BaseModel)
                    else item
                    for item in value
                ]
            elif isinstance(value, BaseModel):
                if hasattr(value, "__root__"):
                    normalized[key] = getattr(value, "__root__")
                else:
                    normalized[key] = value.dict(exclude_none=True)
            else:
                normalized[key] = value
        return normalized


@dataclass(frozen=True)
class _SettingDefinition:
    scope: str  # "global", "tenant", "both"


_SETTING_REGISTRY: Dict[str, _SettingDefinition] = {
    "grafana.url": _SettingDefinition(scope="global"),
    "grafana.dashboard_uid": _SettingDefinition(scope="global"),
    "grafana.datasource_uid": _SettingDefinition(scope="global"),
    "theme.colors.primary": _SettingDefinition(scope="global"),
    "email.redirect.enabled": _SettingDefinition(scope="global"),
    "email.redirect.to": _SettingDefinition(scope="global"),
    "networking.plan.targets": _SettingDefinition(scope="both"),
    "networking.dhcp.scopes": _SettingDefinition(scope="both"),
    "networking.dhcp.source": _SettingDefinition(scope="both"),
    "features": _SettingDefinition(scope="both"),
    "worker.enabled": _SettingDefinition(scope="global"),
    "tenant.mode": _SettingDefinition(scope="global"),
    "onboarding.done": _SettingDefinition(scope="global"),
}


def _assert_scope_allowed(key: str, tenant_id: Optional[int]) -> None:
    scope = _SETTING_REGISTRY.get(key)
    if not scope:
        raise HTTPException(status_code=422, detail=[{"loc": [key], "msg": "Unknown setting key", "type": "value_error"}])
    if scope.scope == "global" and tenant_id is not None:
        raise HTTPException(status_code=403, detail=f"Setting '{key}' can only be modified globally")
    if scope.scope == "tenant" and tenant_id is None:
        raise HTTPException(status_code=403, detail=f"Setting '{key}' requires a tenant context")


def _compute_full_payload(db: Session, tenant_id: Optional[int]) -> List[dict]:
    query = db.query(AppSetting)
    if tenant_id is None:
        query = query.filter(AppSetting.tenant_id.is_(None))
    else:
        query = query.filter(AppSetting.tenant_id == tenant_id)
    rows = query.order_by(AppSetting.key.asc()).all()
    serialized = []
    for row in rows:
        normalized_value = _normalize_value(row.key, row.value)
        serialized.append(_serialize(row, value=normalized_value))
    return serialized


def _normalize_value(key: str, value: Any) -> Any:
    if key not in _SETTING_REGISTRY:
        return value
    try:
        parsed = _AppSettingsPayload.parse_obj({key: value})
    except ValidationError:
        return value
    return parsed.to_updates().get(key, value)


def _apply_updates(
    db: Session,
    tenant_id: Optional[int],
    updates: Dict[str, Any],
) -> Tuple[List[AppSetting], List[Tuple[str, Any, Any]]]:
    changes: List[Tuple[str, Any, Any]] = []
    affected: Dict[str, AppSetting] = {}
    try:
        for key, new_value in updates.items():
            _assert_scope_allowed(key, tenant_id)
            query = db.query(AppSetting)
            if tenant_id is None:
                query = query.filter(AppSetting.tenant_id.is_(None))
            else:
                query = query.filter(AppSetting.tenant_id == tenant_id)
            existing = query.filter(AppSetting.key == key).one_or_none()
            previous_value = existing.value if existing else None
            if new_value is None:
                if existing:
                    db.delete(existing)
                    changes.append((key, previous_value, None))
                continue
            if existing:
                if existing.value != new_value:
                    existing.value = new_value
                    changes.append((key, previous_value, new_value))
                affected[key] = existing
            else:
                created = AppSetting(tenant_id=tenant_id, key=key, value=new_value)
                db.add(created)
                db.flush()
                affected[key] = created
                changes.append((key, None, new_value))
        db.commit()
    except Exception:
        db.rollback()
        raise
    refreshed: List[AppSetting] = []
    for item in affected.values():
        db.refresh(item)
        refreshed.append(item)
    return refreshed, changes


def _is_settings_feature_enabled(db: Session, user: User) -> bool:
    def _resolve_flag(scope_query: Iterable[AppSetting]) -> Optional[bool]:
        resolved: Optional[bool] = None
        for row in scope_query:
            if row.key == "features" and isinstance(row.value, dict):
                if "settings" in row.value:
                    resolved = bool(row.value["settings"])
            elif row.key == "features.settings":
                resolved = bool(row.value)
        return resolved

    global_rows = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None))
        .filter(AppSetting.key.in_(["features", "features.settings"]))
        .all()
    )
    flag = _resolve_flag(global_rows)
    if user.tenant_id is not None:
        tenant_rows = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == user.tenant_id)
            .filter(AppSetting.key.in_(["features", "features.settings"]))
            .all()
        )
        tenant_flag = _resolve_flag(tenant_rows)
        if tenant_flag is not None:
            flag = tenant_flag
    return True if flag is None else bool(flag)


@router.get("", response_model=List[dict])
def list_global_settings(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> List[dict] | Response:
    payload = _compute_full_payload(db, tenant_id=None)
    conditional = _apply_conditional_headers(request, response, payload)
    if conditional is not None:
        return conditional  # type: ignore[return-value]
    return payload


@router.put("", response_model=List[dict])
def upsert_global_settings(
    payload: Dict[str, object],
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> List[dict]:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Expected JSON object of key->value pairs")
    if not _is_settings_feature_enabled(db, current_user):
        raise HTTPException(status_code=403, detail="Settings management is disabled for this tenant")
    try:
        validated = _AppSettingsPayload.parse_obj(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())
    updates = validated.to_updates()
    updated_rows, changes = _apply_updates(db, tenant_id=None, updates=updates)
    full_payload = _compute_full_payload(db, tenant_id=None)
    if full_payload:
        response.headers["ETag"] = _compute_etag(full_payload)
    response.headers.setdefault("Cache-Control", "no-cache")
    if changes:
        log_audit_event(
            db,
            user_id=current_user.id,
            action="app_settings.update",
            result="success",
            ip=None,
            details={
                "scope": "global",
                "changes": [
                    {"key": key, "previous": old, "current": new}
                    for key, old, new in changes
                ],
            },
        )
    # Return the entries affected so the UI can refresh quickly; the GET response still exposes the full list.
    if updated_rows:
        return [_serialize(r) for r in updated_rows]
    return []


@router.get("/tenant", response_model=List[dict])
def list_tenant_settings(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user),
) -> List[dict] | Response:
    payload = _compute_full_payload(db, tenant_id=user.tenant_id)
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
    if not _is_settings_feature_enabled(db, user):
        raise HTTPException(status_code=403, detail="Settings management is disabled for this tenant")
    try:
        validated = _AppSettingsPayload.parse_obj(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())
    updates = validated.to_updates()
    updated_rows, changes = _apply_updates(db, tenant_id=user.tenant_id, updates=updates)
    tenant_key = str(user.tenant_id) if user.tenant_id is not None else "global"
    full_payload = _compute_full_payload(db, tenant_id=user.tenant_id)
    if full_payload:
        response.headers["ETag"] = _compute_etag(full_payload, tenant_key=tenant_key)
    response.headers.setdefault("Cache-Control", "no-cache")
    if changes:
        log_audit_event(
            db,
            user_id=user.id,
            action="app_settings.update",
            result="success",
            ip=None,
            details={
                "scope": "tenant",
                "tenant_id": user.tenant_id,
                "changes": [
                    {"key": key, "previous": old, "current": new}
                    for key, old, new in changes
                ],
            },
        )
    if updated_rows:
        return [_serialize(r) for r in updated_rows]
    return []
