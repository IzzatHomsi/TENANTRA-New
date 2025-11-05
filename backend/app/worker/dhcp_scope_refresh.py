"""Background worker that refreshes DHCP scope data from Infoblox/HTTP sources."""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, Iterable, List, Optional

from app.db.session import get_db_session
from app.models.app_setting import AppSetting
from app.models.tenant import Tenant
from app.services.modules.dhcp_scope_capacity_guard import _fetch_scopes_from_source

LOG = logging.getLogger("tenantra.dhcp.worker")


def _resolve_app_setting(db, tenant_id: Optional[int], key: str) -> Optional[AppSetting]:
    """Return tenant-specific app setting, falling back to global."""
    if tenant_id is not None:
        row = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == tenant_id, AppSetting.key == key)
            .order_by(AppSetting.id.desc())
            .first()
        )
        if row:
            return row
    return (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None), AppSetting.key == key)
        .order_by(AppSetting.id.desc())
        .first()
    )


def _ensure_app_setting(db, tenant_id: int, key: str, value: Any) -> AppSetting:
    row = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id == tenant_id, AppSetting.key == key)
        .first()
    )
    if row:
        row.value = value
        return row
    row = AppSetting(tenant_id=tenant_id, key=key, value=value)
    db.add(row)
    return row


class DHCPScopeRefreshWorker:
    """Fetch DHCP scope telemetry and cache in AppSettings for module consumption."""

    def __init__(self, poll_interval_seconds: int = 300) -> None:
        self.poll_interval_seconds = max(poll_interval_seconds, 60)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            LOG.info("DHCP scope refresh worker already running.")
            return
        self._thread = threading.Thread(
            target=self._run_loop,
            name="dhcp-scope-refresh",
            daemon=True,
        )
        self._thread.start()
        LOG.info("DHCP scope refresh worker started (interval=%ss).", self.poll_interval_seconds)

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                LOG.warning("DHCP scope refresh worker did not stop within timeout.")
            else:
                LOG.info("DHCP scope refresh worker stopped.")
        self._thread = None
        self._stop_event.clear()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.process_once()
            except Exception:
                LOG.exception("DHCP scope refresh iteration failed.")
            self._stop_event.wait(timeout=self.poll_interval_seconds)

    def process_once(self) -> None:
        """Refresh scope telemetry for all tenants."""
        with get_db_session() as db:
            tenants: List[Tenant] = db.query(Tenant).all()
            if not tenants:
                return
            for tenant in tenants:
                source_setting = _resolve_app_setting(db, tenant.id, "networking.dhcp.source")
                source_cfg = source_setting.value if source_setting and isinstance(source_setting.value, dict) else None
                if not source_cfg:
                    continue
                source_type = str(source_cfg.get("type") or "manual").lower()
                if source_type not in {"infoblox", "http", "https"}:
                    continue
                scopes = _fetch_scopes_from_source(source_cfg)
                if not scopes:
                    continue
                scopes_payload: List[Dict[str, Any]] = [
                    {
                        "name": scope.name,
                        "total_leases": scope.total,
                        "active_leases": scope.used,
                        "reserved_leases": scope.reserved,
                        "dhcp_server": scope.dhcp_server,
                        "site": scope.site,
                        "vlan": scope.vlan,
                        "tags": list(scope.tags) if scope.tags else [],
                        "threshold_warn": scope.threshold_warn,
                        "threshold_crit": scope.threshold_crit,
                    }
                    for scope in scopes
                ]
                _ensure_app_setting(db, tenant.id, "networking.dhcp.scopes", scopes_payload)
                LOG.debug("Updated DHCP scopes for tenant_id=%s (scopes=%s)", tenant.id, len(scopes_payload))
            db.commit()
