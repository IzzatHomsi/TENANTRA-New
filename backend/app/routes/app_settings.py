from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import hashlib
import json
import copy
import threading
from contextlib import nullcontext

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
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

from app.core.auth import get_admin_user, get_settings_user
from app.database import get_db
from app.models.app_setting import AppSetting
from app.models.user import User
from app.utils.audit import log_audit_event
from app.services.feature_flags import (
    ensure_settings_read_access,
    ensure_settings_write_access,
)
from app.core.crypto import encrypt_data
from app.core.secrets import get_enc_key

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])


try:
    from opentelemetry import trace as otel_trace

    _TRACER = otel_trace.get_tracer(__name__)
except Exception:  # pragma: no cover - optional dependency
    _TRACER = None


def _span(name: str):
    if _TRACER:
        return _TRACER.start_as_current_span(name)
    return nullcontext()


_SETTINGS_CACHE: Dict[str, Tuple[List[dict], str]] = {}
_SETTINGS_CACHE_LOCK = threading.Lock()


def _cache_key(tenant_id: Optional[int]) -> str:
    return "global" if tenant_id is None else f"tenant:{tenant_id}"


def _get_cached_settings(tenant_id: Optional[int]) -> Optional[Tuple[List[dict], str]]:
    key = _cache_key(tenant_id)
    with _SETTINGS_CACHE_LOCK:
        entry = _SETTINGS_CACHE.get(key)
    if not entry:
        return None
    payload, etag = entry
    return copy.deepcopy(payload), etag


def _set_cached_settings(tenant_id: Optional[int], payload: List[dict], etag: str) -> None:
    key = _cache_key(tenant_id)
    with _SETTINGS_CACHE_LOCK:
        _SETTINGS_CACHE[key] = (copy.deepcopy(payload), etag)


def _invalidate_cache(*tenant_ids: Optional[int]) -> None:
    with _SETTINGS_CACHE_LOCK:
        if not tenant_ids:
            _SETTINGS_CACHE.clear()
            return
        for tenant_id in tenant_ids:
            _SETTINGS_CACHE.pop(_cache_key(tenant_id), None)


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
    etag: Optional[str] = None,
) -> Optional[Response]:
    etag = etag or _compute_etag(items, tenant_key)
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

    @root_validator(skip_on_failure=True)
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


class _AppSettingsPayload(BaseModel):
    grafana_url: Optional[str] = Field(None, alias="grafana.url")
    grafana_dashboard_uid: Optional[constr(strip_whitespace=True, min_length=2, max_length=120, pattern=r"^[A-Za-z0-9_\-]+$")] = Field(
        None, alias="grafana.dashboard_uid"
    )
    grafana_datasource_uid: Optional[constr(strip_whitespace=True, min_length=2, max_length=120, pattern=r"^[A-Za-z0-9_\-]+$")] = Field(
        None, alias="grafana.datasource_uid"
    )
    theme_color_primary: Optional[constr(strip_whitespace=True, pattern=r"^#[0-9A-Fa-f]{6}$")] = Field(
        None, alias="theme.colors.primary"
    )
    email_redirect_enabled: Optional[bool] = Field(None, alias="email.redirect.enabled")
    email_redirect_to: Optional[EmailStr] = Field(None, alias="email.redirect.to")
    networking_plan_targets: Optional[List[_PortTarget]] = Field(None, alias="networking.plan.targets")
    networking_dhcp_scopes: Optional[List[_DHCPScope]] = Field(None, alias="networking.dhcp.scopes")
    networking_dhcp_source: Optional[_DHCPSource] = Field(None, alias="networking.dhcp.source")
    feature_flags: Optional[Dict[str, bool]] = Field(None, alias="features")
    worker_enabled: Optional[bool] = Field(None, alias="worker.enabled")
    tenant_mode: Optional[constr(strip_whitespace=True, to_lower=True)] = Field(None, alias="tenant.mode")
    onboarding_done: Optional[bool] = Field(None, alias="onboarding.done")
    grafana_proxy_max_body_bytes: Optional[int] = Field(None, alias="grafana.proxy.max_body_bytes")
    grafana_proxy_max_requests_per_minute: Optional[int] = Field(None, alias="grafana.proxy.max_requests_per_minute")
    grafana_basic_username: Optional[constr(strip_whitespace=True, min_length=1, max_length=120)] = Field(
        None, alias="grafana.basic.username"
    )
    grafana_basic_password: Optional[str] = Field(None, alias="grafana.basic.password")

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

    @validator("grafana_proxy_max_body_bytes", pre=True)
    def _sanitize_proxy_limit(cls, value: Optional[object]) -> Optional[int]:
        if value in (None, "", False):
            return None
        try:
            limit = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise ValueError("grafana.proxy.max_body_bytes must be an integer")
        if limit <= 0:
            raise ValueError("grafana.proxy.max_body_bytes must be greater than zero")
        return limit

    @validator("grafana_proxy_max_requests_per_minute", pre=True)
    def _sanitize_proxy_rate(cls, value: Optional[object]) -> Optional[int]:
        if value in (None, "", False):
            return None
        try:
            limit = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise ValueError("grafana.proxy.max_requests_per_minute must be an integer")
        if limit < 0:
            raise ValueError("grafana.proxy.max_requests_per_minute must be non-negative")
        return limit

    @validator("grafana_basic_username", pre=True)
    def _strip_username(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @validator("grafana_basic_password", pre=True)
    def _clean_password(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @validator("networking_plan_targets", "networking_dhcp_scopes", pre=True)
    def _allow_empty_iterable(cls, value: Optional[Iterable[Any]]) -> Optional[Iterable[Any]]:
        if value is None:
            return None
        if isinstance(value, list) and len(value) == 0:
            return []
        return value

    @validator("feature_flags", pre=True)
    def _normalize_features(cls, value: Optional[Dict[str, Any]]) -> Optional[Dict[str, bool]]:
        if value in (None, "", False):
            return None
        if not isinstance(value, dict):
            raise ValueError("features must be a JSON object of feature->enabled flags")
        normalized: Dict[str, bool] = {}
        for key, raw in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Feature keys must be non-empty strings")
            normalized[key.strip()] = bool(raw)
        return normalized or None

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
                normalized[key] = value.dict(exclude_none=True)
            elif key == "grafana.basic.password":
                if value is None:
                    normalized[key] = None
                else:
                    ciphertext = encrypt_data(value, get_enc_key())
                    normalized[key] = {"ciphertext": ciphertext, "set": True}
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
    "grafana.proxy.max_body_bytes": _SettingDefinition(scope="global"),
    "grafana.proxy.max_requests_per_minute": _SettingDefinition(scope="global"),
    "grafana.basic.username": _SettingDefinition(scope="global"),
    "grafana.basic.password": _SettingDefinition(scope="global"),
}


def _assert_scope_allowed(key: str, tenant_id: Optional[int]) -> None:
    scope = _SETTING_REGISTRY.get(key)
    if not scope:
        raise HTTPException(status_code=422, detail=[{"loc": [key], "msg": "Unknown setting key", "type": "value_error"}])
    if scope.scope == "global" and tenant_id is not None:
        raise HTTPException(status_code=403, detail=f"Setting '{key}' can only be modified globally")
    if scope.scope == "tenant" and tenant_id is None:
        raise HTTPException(status_code=403, detail=f"Setting '{key}' requires a tenant context")


def _get_settings_payload(db: Session, tenant_id: Optional[int]) -> Tuple[List[dict], str]:
    cached = _get_cached_settings(tenant_id)
    if cached:
        return cached
    query = db.query(AppSetting)
    if tenant_id is None:
        query = query.filter(AppSetting.tenant_id.is_(None))
    else:
        query = query.filter(AppSetting.tenant_id == tenant_id)
    rows = query.order_by(AppSetting.key.asc()).all()
    serialized: List[dict] = []
    for row in rows:
        normalized_value = _normalize_value(row.key, row.value)
        serialized.append(_serialize(row, value=normalized_value))
    tenant_key = str(tenant_id) if tenant_id is not None else None
    etag = _compute_etag(serialized, tenant_key)
    _set_cached_settings(tenant_id, serialized, etag)
    return serialized, etag


def _serialize_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sanitized: List[Dict[str, Any]] = []
    for entry in errors:
        item = dict(entry)
        ctx = item.get("ctx")
        if isinstance(ctx, dict):
            clean_ctx: Dict[str, Any] = {}
            for key, raw in ctx.items():
                clean_ctx[key] = str(raw) if isinstance(raw, Exception) else raw
            item["ctx"] = clean_ctx
        sanitized.append(item)
    return sanitized


def _normalize_value(key: str, value: Any) -> Any:
    if key == "grafana.basic.password":
        if isinstance(value, dict):
            return {"set": bool(value.get("ciphertext"))}
        return None
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


@router.get("", response_model=List[dict])
def list_global_settings(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_settings_user),
) -> List[dict] | Response:
    with _span("app_settings.list_global"):
        try:
            ensure_settings_read_access(db, current_user)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        payload, etag = _get_settings_payload(db, tenant_id=None)
        conditional = _apply_conditional_headers(request, response, payload, etag=etag)
        if conditional is not None:
            return conditional  # type: ignore[return-value]
        response.headers["ETag"] = etag
        response.headers.setdefault("Cache-Control", "no-cache")
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
    with _span("app_settings.upsert_global"):
        try:
            ensure_settings_write_access(db, current_user)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        try:
            validated = _AppSettingsPayload.parse_obj(payload)
        except ValidationError as exc:
            return JSONResponse(
                status_code=422,
                content=_serialize_validation_errors(exc.errors()),
            )
        updates = validated.to_updates()
        updated_rows, changes = _apply_updates(db, tenant_id=None, updates=updates)
        if changes:
            change_entries = [
                {"key": key, "previous": old, "current": new}
                for key, old, new in changes
            ]
            flat_lookup = {entry["key"]: {"previous": entry["previous"], "current": entry["current"]} for entry in change_entries}
            log_audit_event(
                db,
                user_id=current_user.id,
                action="app_settings.update",
                result="success",
                ip=None,
                details={
                    "scope": "global",
                    "changes": change_entries,
                    **flat_lookup,
                },
            )
        _invalidate_cache()
        payload_snapshot, etag = _get_settings_payload(db, tenant_id=None)
        response.headers["ETag"] = etag
        response.headers.setdefault("Cache-Control", "no-cache")
        return payload_snapshot


@router.get("/tenant", response_model=List[dict])
def list_tenant_settings(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_settings_user),
) -> List[dict] | Response:
    with _span("app_settings.list_tenant"):
        try:
            ensure_settings_read_access(db, user)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        payload, etag = _get_settings_payload(db, tenant_id=user.tenant_id)
        tenant_key = str(user.tenant_id) if user.tenant_id is not None else None
        conditional = _apply_conditional_headers(request, response, payload, tenant_key=tenant_key, etag=etag)
        if conditional is not None:
            return conditional  # type: ignore[return-value]
        response.headers["ETag"] = etag
        response.headers.setdefault("Cache-Control", "no-cache")
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
    with _span("app_settings.upsert_tenant"):
        try:
            ensure_settings_write_access(db, user)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        try:
            validated = _AppSettingsPayload.parse_obj(payload)
        except ValidationError as exc:
            return JSONResponse(
                status_code=422,
                content=_serialize_validation_errors(exc.errors()),
            )
        updates = validated.to_updates()
        updated_rows, changes = _apply_updates(db, tenant_id=user.tenant_id, updates=updates)
        if changes:
            change_entries = [
                {"key": key, "previous": old, "current": new}
                for key, old, new in changes
            ]
            flat_lookup = {entry["key"]: {"previous": entry["previous"], "current": entry["current"]} for entry in change_entries}
            log_audit_event(
                db,
                user_id=user.id,
                action="app_settings.update",
                result="success",
                ip=None,
                details={
                    "scope": "tenant",
                    "tenant_id": user.tenant_id,
                    "changes": change_entries,
                    **flat_lookup,
                },
            )
        _invalidate_cache(user.tenant_id)
        payload_snapshot, etag = _get_settings_payload(db, tenant_id=user.tenant_id)
        response.headers["ETag"] = etag
        response.headers.setdefault("Cache-Control", "no-cache")
        return payload_snapshot
