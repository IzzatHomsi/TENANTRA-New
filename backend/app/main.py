"""FastAPI application entrypoint for Tenantra."""

from __future__ import annotations

import logging
import logging.config
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def _init_logging() -> None:
    try:
        import app.logging_conf as lc  # type: ignore
        if hasattr(lc, "configure_logging"):
            lc.configure_logging()  # type: ignore[attr-defined]
            return
        if hasattr(lc, "LOGGING_CONFIG"):
            logging.config.dictConfig(getattr(lc, "LOGGING_CONFIG"))  # type: ignore[arg-type]
            return
    except Exception as exc:
        logging.basicConfig(
            level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
        logging.getLogger(__name__).warning("Logging fallback initialized: %s", exc)


from app.bootstrap import bootstrap_test_data
from app.middleware.correlation_id import CorrelationIdMiddleware  # type: ignore
from app.middleware.request_logging import RequestLoggingMiddleware  # type: ignore
from app.middleware.security_headers import SecurityHeadersMiddleware  # type: ignore
from app.middleware.dynamic_cors import DynamicCORSMiddleware  # type: ignore
from app.middleware.rate_limit import RateLimitMiddleware  # type: ignore
from app.observability.metrics import request_metrics_middleware  # type: ignore
from app.worker.notifications_worker import NotificationsWorker  # type: ignore
from app.worker.module_scheduler import ModuleSchedulerWorker  # type: ignore
from app.worker.dhcp_scope_refresh import DHCPScopeRefreshWorker  # type: ignore

# Ensure all SQLAlchemy models are registered at import time so that string-based
# relationship() declarations resolve properly during mapper configuration.
import app.models  # noqa: F401


logger = logging.getLogger("tenantra.main")


def _maybe_import_modules() -> None:
    """Optionally import modules from the backlog CSV on startup."""
    flag = os.getenv("TENANTRA_AUTO_IMPORT_MODULES", os.getenv("TENANTRA_IMPORT_MODULES", "1")).strip().lower()
    if flag not in {"1", "true", "yes", "on"}:
        logger.info("Auto module import disabled (TENANTRA_AUTO_IMPORT_MODULES=%s).", flag)
        return
    try:
        try:
            from app.scripts.import_modules_from_csv import import_modules as _import_modules  # type: ignore
        except Exception:
            from scripts.import_modules_from_csv import import_modules as _import_modules  # type: ignore
        from pathlib import Path
        candidates = []
        configured = os.getenv("TENANTRA_MODULES_CSV")
        if configured:
            candidates.append(Path(configured))
        repo_root = Path(__file__).resolve().parents[2]
        candidates.extend(
            [
                repo_root / "docs" / "modules" / "Tenantra_Module_Backlog_PhaseLinked_v8.csv",
                Path.cwd() / "docs" / "modules" / "Tenantra_Module_Backlog_PhaseLinked_v8.csv",
                Path("/app/docs/modules/Tenantra_Module_Backlog_PhaseLinked_v8.csv"),
            ]
        )
        csv_path = next((p for p in candidates if p.exists()), None)
        if not csv_path:
            logger.warning("Module CSV not found; skipping auto-import (candidates=%s)", candidates)
            return
        stats = _import_modules(csv_path)
        logger.info("Module auto-import completed using %s: %s", csv_path, stats)
    except Exception:
        logger.exception("Module auto-import failed")


def create_app() -> FastAPI:
    _init_logging()
    app = FastAPI(title="Tenantra Backend", version=os.getenv("APP_VERSION", "1.0"))

    # Middlewares
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(DynamicCORSMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Metrics
    app.middleware("http")(request_metrics_middleware())

    def _include_if_exists(module_path: str, prefix: str) -> None:
        """Import `<module_path>.router` if present and include it with `prefix`."""
        try:
            mod = __import__(module_path, fromlist=["router"])
            router = getattr(mod, "router", None)
            if router is not None:
                app.include_router(router, prefix=prefix)
        except Exception as exc:
            logger.info("Router not included (%s): %s", module_path, exc)

    # Route modules mounted at root and /api
    ROUTE_MODULES = [
        "app.routes.health",
        "app.routes.healthz",
        "app.routes.auth",
        # Use the unified users_me routes for self-service profile endpoints
        # (avoid duplicate /users/me handlers from app.routes.users)
        # "app.routes.users",
        "app.routes.users_me",
        "app.routes.users_admin",
        "app.routes.tenants_admin",
        "app.routes.modules",
        "app.routes.module_mapping",
        "app.routes.module_runs",
        "app.routes.schedules",
        "app.routes.integrity",
        "app.routes.compliance",
        "app.routes.compliance_export",
        "app.routes.export",
        "app.routes.assets",
        "app.routes.visibility",
        "app.routes.tenant_example",
        "app.routes.notifications",
        "app.routes.notification_history",
        "app.routes.notification_settings",
        "app.routes.notification_prefs",
        "app.routes.audit_logs",
        "app.routes.alerts",
        "app.routes.agents",
        "app.routes.agents_admin",
        "app.routes.agent_logs",
        "app.routes.roles",
        "app.routes.processes",
        "app.routes.scan_results",
        "app.routes.logs",
        "app.routes.metrics",
        # support CTA + settings/admin/public mounted at app level
        "app.routes.support",
        "app.routes.app_settings",
        "app.routes.modules_admin",
        "app.routes.app_logs",
        "app.routes.observability_admin",
        "app.routes.public_settings",
        "app.routes.grafana_proxy",
        "app.routes.network_admin",
        "app.routes.plan_presets",
        "app.routes.features",
        "app.routes.telemetry",
    ]

    for mod in ROUTE_MODULES:
        _include_if_exists(mod, "")
        # Avoid duplicating routes like grafana proxy under /api, which causes OpenAPI warnings
        if mod != "app.routes.grafana_proxy":
            _include_if_exists(mod, "/api")

    # Ensure scan orchestration router is mounted under /api explicitly (some environments skip the generic include)
    try:
        from app.routes import scan_orchestration as _scan_orch  # type: ignore
        if getattr(_scan_orch, "router", None) is not None:
            app.include_router(_scan_orch.router, prefix="/api")
    except Exception as exc:
        logger.info("Explicit include for scan_orchestration under /api failed: %s", exc)

    # Background workers (opt-in)
    worker: Optional[NotificationsWorker] = None
    scheduler_worker: Optional[ModuleSchedulerWorker] = None
    dhcp_worker: Optional[DHCPScopeRefreshWorker] = None

    @app.on_event("startup")
    def _start_worker() -> None:
        nonlocal worker, scheduler_worker, dhcp_worker
        # Lightweight bootstrap for local/tests: create tables + seed admin if requested
        # This is gated by TENANTRA_TEST_BOOTSTRAP to avoid affecting normal runs.
        bootstrap_test_data()
        _maybe_import_modules()
        notif_flag = os.getenv("TENANTRA_ENABLE_NOTIFICATIONS_WORKER", "0").strip().lower()
        if notif_flag in {"1", "true", "yes", "on"}:
            try:
                worker = NotificationsWorker()
                worker.start()
                logger.info("Notifications worker started.")
            except Exception:
                logger.exception("Failed to start notifications worker.")
        scheduler_flag = os.getenv("TENANTRA_ENABLE_MODULE_SCHEDULER", "0").strip().lower()
        if scheduler_flag in {"1", "true", "yes", "on"}:
            try:
                interval = float(os.getenv("TENANTRA_SCHEDULER_INTERVAL", "30"))
                scheduler_worker = ModuleSchedulerWorker(poll_interval=max(interval, 5.0))
                scheduler_worker.start()
                logger.info("Module scheduler worker started (interval=%ss).", scheduler_worker.poll_interval)
            except Exception:
                logger.exception("Failed to start module scheduler worker.")
        dhcp_flag = os.getenv("TENANTRA_ENABLE_DHCP_REFRESH_WORKER", "0").strip().lower()
        if dhcp_flag in {"1", "true", "yes", "on"}:
            try:
                interval = float(os.getenv("TENANTRA_DHCP_REFRESH_INTERVAL", "300"))
                dhcp_worker = DHCPScopeRefreshWorker(poll_interval_seconds=max(interval, 60))
                dhcp_worker.start()
                logger.info("DHCP scope refresh worker started (interval=%ss).", dhcp_worker.poll_interval_seconds)
            except Exception:
                logger.exception("Failed to start DHCP scope refresh worker.")

    @app.on_event("shutdown")
    def _stop_worker() -> None:
        nonlocal worker, scheduler_worker, dhcp_worker
        if worker:
            try:
                worker.stop(timeout=5.0)
            except Exception:
                logger.exception("Error stopping notifications worker.")
            finally:
                worker = None
        if scheduler_worker:
            try:
                scheduler_worker.stop(timeout=5.0)
            except Exception:
                logger.exception("Error stopping module scheduler worker.")
            finally:
                scheduler_worker = None
        if dhcp_worker:
            try:
                dhcp_worker.stop(timeout=5.0)
            except Exception:
                logger.exception("Error stopping DHCP scope refresh worker.")
            finally:
                dhcp_worker = None

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
            description="Tenantra API",
        )
        components = openapi_schema.setdefault("components", {})
        components["securitySchemes"] = {"BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}
        for _path, methods in openapi_schema.get("paths", {}).items():
            for _method, op in methods.items():
                op.setdefault("security", [{"BearerAuth": []}])
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    return app


app = create_app()
