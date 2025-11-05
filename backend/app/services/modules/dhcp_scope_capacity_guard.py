"""Module runner for DHCP scope capacity monitoring."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
from requests import RequestException

from app.database import SessionLocal
from app.models.app_setting import AppSetting
from app.services.module_runner import ModuleContext, ModuleExecutionResult, ModuleRunner, build_result

LOG = logging.getLogger(__name__)


@dataclass
class ScopeRecord:
    name: str
    total: int
    used: int
    reserved: int = 0
    dhcp_server: Optional[str] = None
    site: Optional[str] = None
    vlan: Optional[str] = None
    tags: Optional[Iterable[str]] = None
    threshold_warn: Optional[float] = None
    threshold_crit: Optional[float] = None

    def utilization(self) -> Tuple[int, float, float]:
        total = max(self.total, 1)
        used = max(min(self.used, total), 0)
        free = max(total - used, 0)
        free_pct = (free / total) * 100.0
        used_pct = (used / total) * 100.0
        return free, free_pct, used_pct


def _optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _hydrate_scope(raw: Dict[str, Any]) -> Optional[ScopeRecord]:
    name = str(raw.get("name") or raw.get("scope") or "").strip()
    if not name:
        return None
    try:
        total = int(raw.get("total_leases") or raw.get("total") or raw.get("capacity") or 0)
        used = int(raw.get("active_leases") or raw.get("used") or raw.get("leases_used") or 0)
    except (TypeError, ValueError):
        return None
    reserved_raw = raw.get("reserved_leases") or raw.get("reserved") or 0
    try:
        reserved = int(reserved_raw)
    except (TypeError, ValueError):
        reserved = 0
    return ScopeRecord(
        name=name,
        total=max(total, 0),
        used=max(used, 0),
        reserved=max(reserved, 0),
        dhcp_server=raw.get("dhcp_server") or raw.get("server"),
        site=raw.get("site") or raw.get("location"),
        vlan=raw.get("vlan") or raw.get("network"),
        tags=raw.get("tags"),
        threshold_warn=_optional_float(raw.get("threshold_warn")),
        threshold_crit=_optional_float(raw.get("threshold_crit")),
    )


def _load_scopes_from_settings(tenant_id: Optional[int]) -> List[ScopeRecord]:
    session = SessionLocal()
    try:
        query = session.query(AppSetting).filter(AppSetting.key == "networking.dhcp.scopes")
        settings = query.filter(
            (AppSetting.tenant_id == tenant_id) | (AppSetting.tenant_id.is_(None))
        ).order_by(AppSetting.tenant_id.desc()).all() if tenant_id is not None else query.filter(
            AppSetting.tenant_id.is_(None)
        ).all()
        for setting in settings:
            if isinstance(setting.value, list):
                scopes: List[ScopeRecord] = []
                for item in setting.value:
                    if isinstance(item, dict):
                        scope = _hydrate_scope(item)
                        if scope:
                            scopes.append(scope)
                if scopes:
                    return scopes
        return []
    finally:
        session.close()


def _sanitize_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    sanitized: Dict[str, Any] = {}
    for key, value in parameters.items():
        if key == "source" and isinstance(value, dict):
            sanitized["source"] = {
                k: v
                for k, v in value.items()
                if k.lower() not in {"password", "token", "api_key", "api-key", "secret"}
            }
        else:
            sanitized[key] = value
    return sanitized


def _fetch_scopes_from_source(source_cfg: Dict[str, Any]) -> List[ScopeRecord]:
    source_type = str(source_cfg.get("type") or "manual").lower()
    if source_type not in {"infoblox", "http", "https"}:
        return []
    endpoint = source_cfg.get("endpoint") or source_cfg.get("url")
    if not endpoint:
        return []

    headers: Dict[str, str] = {}
    auth = None
    if source_cfg.get("api_key"):
        headers["Authorization"] = f"Bearer {source_cfg['api_key']}"
    username = source_cfg.get("username")
    password = source_cfg.get("password")
    if username and password:
        auth = (username, password)
    timeout = float(source_cfg.get("timeout_seconds") or 10.0)
    verify = bool(source_cfg.get("verify_tls", True))

    try:
        resp = requests.get(str(endpoint), headers=headers, auth=auth, timeout=timeout, verify=verify)
        resp.raise_for_status()
        payload = resp.json()
    except RequestException as exc:
        LOG.warning("Failed to fetch DHCP scopes from %s: %s", endpoint, exc)
        return []
    except ValueError:
        LOG.warning("Unexpected DHCP scope payload from %s", endpoint)
        return []

    if isinstance(payload, dict):
        potential = payload.get("data") or payload.get("scopes") or payload.get("results")
        if isinstance(potential, list):
            payload = potential
        else:
            payload = [payload]

    if not isinstance(payload, list):
        return []

    scopes: List[ScopeRecord] = []
    for item in payload:
        if isinstance(item, dict):
            scope = _hydrate_scope(item)
            if scope:
                scopes.append(scope)
    return scopes


def _coerce_float(value: Any, default: float) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        return float(str(value))
    except (TypeError, ValueError):
        return default


class DHCPScopeCapacityGuard(ModuleRunner):
    """Evaluate DHCP scope capacity and flag ranges approaching exhaustion."""

    name = "Networking — DHCP Scope Capacity Guard"
    slug = "dhcp-scope-capacity-guard"
    parameter_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "warn_threshold_pct": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "default": 20,
                "description": "Warn when free leases drop below this percentage.",
            },
            "critical_threshold_pct": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "default": 10,
                "description": "Trigger failure when free leases drop below this percentage.",
            },
            "scopes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "total_leases": {"type": "integer", "minimum": 0},
                        "active_leases": {"type": "integer", "minimum": 0},
                        "reserved_leases": {"type": "integer", "minimum": 0},
                        "dhcp_server": {"type": "string"},
                        "site": {"type": "string"},
                        "vlan": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "threshold_warn": {"type": "number", "minimum": 0, "maximum": 100},
                        "threshold_crit": {"type": "number", "minimum": 0, "maximum": 100},
                    },
                    "required": ["name", "total_leases", "active_leases"],
                },
            },
            "source": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["manual", "infoblox", "http", "https"],
                        "default": "manual",
                    },
                    "endpoint": {"type": "string", "format": "uri"},
                    "url": {"type": "string", "format": "uri"},
                    "api_key": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                    "timeout_seconds": {"type": "number", "minimum": 1, "maximum": 60},
                    "verify_tls": {"type": "boolean", "default": True},
                },
            },
            "force_status": {
                "type": "string",
                "enum": ["success", "failed", "error", "skipped"],
            },
        },
        "additionalProperties": True,
    }

    def run(self, context: ModuleContext) -> ModuleExecutionResult:  # type: ignore[override]
        params: Dict[str, Any] = context.parameters or {}
        warn_threshold = _coerce_float(params.get("warn_threshold_pct"), 20.0)
        crit_threshold = _coerce_float(params.get("critical_threshold_pct"), 10.0)

        scopes = self._load_scope_data(context, params)
        if not scopes:
            details = {
                "module": context.module.name,
                "category": context.module.category,
                "summary": {"scopes_evaluated": 0, "status": "no-data"},
                "warnings": ["No DHCP scope telemetry found via parameters, settings, or source configuration."],
                "parameters": _sanitize_parameters(params),
            }
            return build_result(status="skipped", details=details)

        enriched: List[Dict[str, Any]] = []
        findings: List[Dict[str, Any]] = []
        status = "success"

        for scope in scopes:
            free, free_pct, used_pct = scope.utilization()
            warn = scope.threshold_warn if scope.threshold_warn is not None else warn_threshold
            crit = scope.threshold_crit if scope.threshold_crit is not None else crit_threshold
            warn = min(max(warn, 0.0), 100.0)
            crit = min(max(crit, 0.0), warn)

            severity = "ok"
            recommendation = None
            if free_pct <= crit:
                severity = "critical"
                status = "failed"
                recommendation = "Expand the scope or reclaim unused reservations immediately."
            elif free_pct <= warn:
                severity = "warning"
                if status != "failed":
                    status = "failed"
                recommendation = "Plan for capacity increase or clean-up stale leases."

            scope_info = {
                "name": scope.name,
                "dhcp_server": scope.dhcp_server,
                "site": scope.site,
                "vlan": scope.vlan,
                "tags": list(scope.tags) if scope.tags else [],
                "total_leases": scope.total,
                "active_leases": scope.used,
                "reserved_leases": scope.reserved,
                "free_leases": free,
                "free_percent": round(free_pct, 2),
                "used_percent": round(used_pct, 2),
                "thresholds": {"warn_percent": warn, "critical_percent": crit},
                "status": severity,
            }
            if recommendation:
                scope_info["recommendation"] = recommendation

            enriched.append(scope_info)

            if severity in {"warning", "critical"}:
                findings.append(
                    {
                        "scope": scope.name,
                        "severity": severity,
                        "free_percent": round(free_pct, 2),
                        "free_leases": free,
                        "threshold_warn": warn,
                        "threshold_crit": crit,
                        "dhcp_server": scope.dhcp_server,
                        "site": scope.site,
                        "vlan": scope.vlan,
                    }
                )

        summary = {
            "scopes_evaluated": len(enriched),
            "at_capacity": sum(1 for scope in enriched if scope["status"] == "critical"),
            "needs_attention": sum(1 for scope in enriched if scope["status"] == "warning"),
            "status": status,
        }

        details: Dict[str, Any] = {
            "module": context.module.name,
            "category": context.module.category,
            "summary": summary,
            "scopes": enriched,
            "findings": findings,
            "parameters": _sanitize_parameters(params),
        }

        if status == "success":
            details["message"] = "All DHCP scopes have adequate headroom."

        return build_result(status=status, details=details)

    def _load_scope_data(self, context: ModuleContext, params: Dict[str, Any]) -> List[ScopeRecord]:
        scopes: List[ScopeRecord] = []

        inline_scopes = params.get("scopes")
        if isinstance(inline_scopes, list):
            for item in inline_scopes:
                if isinstance(item, dict):
                    scope = _hydrate_scope(item)
                    if scope:
                        scopes.append(scope)
        if scopes:
            return scopes

        settings_scopes = _load_scopes_from_settings(context.tenant_id)
        if settings_scopes:
            return settings_scopes

        source_cfg = params.get("source")
        if isinstance(source_cfg, dict):
            fetched = _fetch_scopes_from_source(source_cfg)
            if fetched:
                return fetched

        return scopes
