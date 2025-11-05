"""Dynamic CORS middleware."""

import os
import time
from typing import Optional, Set

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

try:
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.tenant_cors_origin import TenantCORSOrigin
except Exception:  # pragma: no cover
    Session = None  # type: ignore
    SessionLocal = None  # type: ignore
    TenantCORSOrigin = None  # type: ignore

CACHE_TTL = int(os.getenv("CORS_DB_CACHE_TTL", "30"))
ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() in ("1", "true", "yes")
ALLOWED_HEADERS = [h.strip() for h in os.getenv("CORS_ALLOWED_HEADERS", "Authorization,Content-Type").split(",") if h.strip()]
ALLOWED_METHODS = [m.strip() for m in os.getenv("CORS_ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",") if m.strip()]

_DEV_DEFAULTS = {
    o.strip()
    for o in os.getenv(
        "TENANTRA_DEV_CORS_DEFAULT",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost,http://127.0.0.1",
    ).split(",")
    if o.strip()
}


class _Cache:
    def __init__(self) -> None:
        self.ts: float = 0.0
        self.origins: Set[str] = set()


_CACHE = _Cache()


def _load_db_origins() -> Set[str]:
    if SessionLocal is None or TenantCORSOrigin is None:
        return set()
    db = SessionLocal()
    try:
        rows = db.query(TenantCORSOrigin).filter(getattr(TenantCORSOrigin, "enabled") == True).all()  # noqa: E712
        return {str(getattr(r, "origin", "")).strip() for r in rows if getattr(r, "origin", "")}
    except Exception:
        return set()
    finally:
        try:
            db.close()
        except Exception:
            pass


def _get_db_origins() -> Set[str]:
    now = time.time()
    if now - _CACHE.ts > CACHE_TTL:
        _CACHE.origins = _load_db_origins()
        _CACHE.ts = now
    return _CACHE.origins


def _env_origins() -> Set[str]:
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
    env_set = {o.strip() for o in raw.split(",") if o.strip()}
    return env_set or _DEV_DEFAULTS


def _is_allowed_origin(origin: Optional[str]) -> bool:
    if not origin:
        return False
    env_set = _env_origins()
    if origin in env_set:
        return True
    db_set = _get_db_origins()
    return origin in db_set


class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        lower_headers = {k.lower(): v for k, v in request.headers.items()}
        is_preflight = request.method == "OPTIONS" and "access-control-request-method" in lower_headers

        allowed_origin: Optional[str] = None
        if _is_allowed_origin(origin):
            allowed_origin = origin
        elif not origin:
            defaults = sorted(_env_origins())
            allowed_origin = defaults[0] if defaults else None

        if is_preflight:
            resp = Response(status_code=204)
        else:
            try:
                resp = await call_next(request)
            except HTTPException as exc:
                detail = exc.detail
                if not isinstance(detail, (dict, list)):
                    detail = {"detail": detail}
                resp = JSONResponse(status_code=exc.status_code, content=detail)
                headers = getattr(exc, "headers", None) or {}
                for key, value in headers.items():
                    resp.headers[key] = value
            except Exception:
                raise

        if allowed_origin:
            resp.headers["Access-Control-Allow-Origin"] = allowed_origin
            if ALLOW_CREDENTIALS:
                resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
            resp.headers["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
            resp.headers["Access-Control-Max-Age"] = os.getenv("CORS_MAX_AGE", "600")
        return resp