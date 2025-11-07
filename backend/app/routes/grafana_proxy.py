from __future__ import annotations

import asyncio
import logging
import os
import time
from collections import deque
from typing import Deque, Dict, Optional, Tuple
from contextlib import nullcontext

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.app_setting import AppSetting
from app.models.user import User
from app.utils.audit import log_audit_event
from app.services.grafana import get_base_url, get_credentials


router = APIRouter()
logger = logging.getLogger(__name__)

_DEFAULT_MAX_PROXY_BODY_BYTES = int(os.getenv("GRAFANA_PROXY_MAX_BODY", str(1 * 1024 * 1024)))  # 1 MiB default
_DEFAULT_RATE_MAX = int(os.getenv("GRAFANA_PROXY_MAX_REQUESTS_PER_MINUTE", "60"))
_DEFAULT_RATE_WINDOW = int(os.getenv("GRAFANA_PROXY_WINDOW_SECONDS", "60"))
PROXY_TIMEOUT = httpx.Timeout(connect=5.0, read=20.0, write=20.0, pool=5.0)

_RATE_LOCK = asyncio.Lock()
_RATE_BUCKETS: Dict[str, Deque[float]] = {}

try:
    from opentelemetry import trace as otel_trace

    _TRACER = otel_trace.get_tracer(__name__)
except Exception:  # pragma: no cover - optional dependency
    _TRACER = None


def _span(name: str):
    if _TRACER:
        return _TRACER.start_as_current_span(name)
    return nullcontext()


def _resolve_max_body_bytes(db: Session) -> int:
    limit = _DEFAULT_MAX_PROXY_BODY_BYTES
    row = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None), AppSetting.key == "grafana.proxy.max_body_bytes")
        .first()
    )
    if row and row.value not in (None, "", False):
        try:
            limit = int(row.value)
        except (TypeError, ValueError):
            logger.warning("Invalid grafana.proxy.max_body_bytes setting; using default", exc_info=False)
    return max(limit, 1)


def _resolve_rate_limit(db: Session) -> Tuple[int, int]:
    limit = _DEFAULT_RATE_MAX
    window = max(_DEFAULT_RATE_WINDOW, 1)
    row = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None), AppSetting.key == "grafana.proxy.max_requests_per_minute")
        .first()
    )
    if row and row.value not in (None, "", False):
        try:
            limit = int(row.value)
        except (TypeError, ValueError):
            logger.warning("Invalid grafana.proxy.max_requests_per_minute; using default", exc_info=False)
    return max(limit, 0), window


async def _enforce_rate_limit(
    db: Session,
    user: User,
    path: str,
    client_host: Optional[str],
) -> None:
    limit, window = _resolve_rate_limit(db)
    if limit <= 0:
        return
    key = f"{user.tenant_id or 'global'}:{user.id}"
    now = time.monotonic()
    async with _RATE_LOCK:
        bucket = _RATE_BUCKETS.setdefault(key, deque())
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= limit:
            log_audit_event(
                db,
                user_id=user.id,
                action="grafana.proxy",
                result="denied",
                ip=client_host,
                details={
                    "reason": "rate-limit",
                    "path": path,
                    "limit": limit,
                    "window_seconds": window,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Grafana proxy rate limit exceeded",
            )
        bucket.append(now)


def _basic_auth_headers(db: Session, tenant_id: Optional[int]) -> Dict[str, str]:
    cred = get_credentials(db, tenant_id=tenant_id)
    if cred:
        user, pw = cred
        from base64 import b64encode

        return {"Authorization": "Basic " + b64encode(f"{user}:{pw}".encode()).decode()}
    user = os.getenv("GRAFANA_USER")
    pw = os.getenv("GRAFANA_PASS")
    user_file = os.getenv("GRAFANA_USER_FILE")
    pass_file = os.getenv("GRAFANA_PASS_FILE")
    try:
        if user_file and not user and os.path.exists(user_file):
            with open(user_file, "r", encoding="utf-8") as f:
                user = f.read().strip()
    except Exception:
        pass
    try:
        if pass_file and not pw and os.path.exists(pass_file):
            with open(pass_file, "r", encoding="utf-8") as f:
                pw = f.read().strip()
    except Exception:
        pass
    if (user or os.getenv("GRAFANA_USER", "")) and not user:
        user = 'admin'
    if user and pw:
        from base64 import b64encode
        return {"Authorization": "Basic " + b64encode(f"{user}:{pw}".encode()).decode()}
    return {}


def _build_upstream(base: str, tail: str, query: str) -> str:
    parsed_base = urlparse(base)
    if parsed_base.scheme not in {"http", "https"} or not parsed_base.netloc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid Grafana base URL")
    clean_tail = tail.lstrip("/")
    if clean_tail and ".." in clean_tail.split("/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path segment")
    upstream = f"{base.rstrip('/')}/{clean_tail}" if clean_tail else base.rstrip("/")
    if query:
        upstream = f"{upstream}?{query}"
    parsed_upstream = urlparse(upstream)
    if parsed_upstream.netloc != parsed_base.netloc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upstream host mismatch")
    return upstream


async def _proxy(db: Session, request: Request, tail: str, user: User) -> Response:
    with _span("grafana.proxy") as span:
        base = get_base_url(db, tenant_id=user.tenant_id)
        if span is not None and base:
            span.set_attribute("grafana.base", base)
        if not base:
            log_audit_event(
                db,
                user_id=user.id,
                action="grafana.proxy",
                result="denied",
                ip=request.client.host if request.client else None,
                details={"reason": "grafana.url not configured"},
            )
            return Response("grafana.url not configured", status_code=404)

        upstream = _build_upstream(base, tail, request.url.query or "")
        proxy_path = f"/grafana/{tail}" if tail else "/grafana"

        hop_by_hop = {
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
            "host",
        }
        headers = {k: v for k, v in request.headers.items() if k.lower() not in hop_by_hop}

        client_host = request.client.host if request.client else None
        if client_host:
            existing_forwarded = headers.get("X-Forwarded-For")
            forwarded_chain = f"{existing_forwarded}, {client_host}" if existing_forwarded else client_host
            headers["X-Forwarded-For"] = forwarded_chain
        if user.tenant_id is not None:
            headers.setdefault("X-Tenant-Id", str(user.tenant_id))
            if span is not None:
                span.set_attribute("tenant.id", user.tenant_id)
        headers.setdefault("X-User-Id", str(user.id))
        headers.setdefault("X-Requested-By", "tenantra-backend")

        body_bytes = b""
        await _enforce_rate_limit(db, user, proxy_path, client_host)

        headers.update(_basic_auth_headers(db, tenant_id=user.tenant_id))

        max_body_bytes = _resolve_max_body_bytes(db)
        content_length_header = request.headers.get("content-length")
        if content_length_header:
            try:
                if int(content_length_header) > max_body_bytes:
                    log_audit_event(
                        db,
                        user_id=user.id,
                        action="grafana.proxy",
                        result="denied",
                        ip=client_host,
                        details={
                            "reason": "payload-too-large",
                            "content_length": int(content_length_header),
                            "limit": max_body_bytes,
                            "path": proxy_path,
                        },
                    )
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Request body exceeds proxy limit")
            except ValueError:
                pass

        body = await request.body()
        body_bytes = body
        if len(body) > max_body_bytes:
            log_audit_event(
                db,
                user_id=user.id,
                action="grafana.proxy",
                result="denied",
                ip=client_host,
                details={
                    "reason": "payload-too-large",
                    "content_length": len(body),
                    "limit": max_body_bytes,
                    "path": proxy_path,
                },
            )
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Request body exceeds proxy limit")

        response: Optional[httpx.Response] = None
        status_code: Optional[int] = None
        ok = False
        error_detail: Optional[str] = None
        try:
            async with httpx.AsyncClient(timeout=PROXY_TIMEOUT, follow_redirects=False) as client:
                response = await client.request(request.method, upstream, content=body_bytes, headers=headers)
            status_code = response.status_code
            ok = 200 <= status_code < 400
            excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
            response_headers = {k: v for k, v in response.headers.items() if k.lower() not in excluded_headers}
            if span is not None:
                span.set_attribute("http.status_code", status_code)
                span.set_attribute("tenantra.grafana.proxy.ok", ok)
            return Response(content=response.content, status_code=status_code, headers=response_headers)
        except httpx.TimeoutException:
            status_code = status.HTTP_504_GATEWAY_TIMEOUT
            error_detail = "Grafana upstream request timed out"
            if span is not None:
                span.record_exception(httpx.TimeoutException(error_detail))
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=error_detail)
        except httpx.HTTPError as exc:
            status_code = status.HTTP_502_BAD_GATEWAY
            error_detail = str(exc)
            if span is not None:
                span.record_exception(exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=error_detail)
        finally:
            try:
                if not (status_code is None and not ok and error_detail is None):
                    log_audit_event(
                        db,
                        user_id=user.id,
                        action="grafana.proxy",
                        result="success" if ok else "failed",
                        ip=client_host,
                        details={
                            "method": request.method,
                            "path": proxy_path,
                            "upstream": upstream,
                            "status": status_code,
                            "tenant_id": user.tenant_id,
                            "bytes": len(body_bytes),
                            "error": error_detail,
                        },
                    )
            except Exception:
                logger.debug("Unable to write Grafana proxy audit log", exc_info=True)


@router.api_route("/grafana", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def grafana_root(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Response:
    return await _proxy(db, request, tail="", user=current_user)


@router.api_route("/grafana/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def grafana_any(
    path: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Response:
    return await _proxy(db, request, tail=path, user=current_user)
