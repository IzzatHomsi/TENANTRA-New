from __future__ import annotations

import logging
import os
from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.app_setting import AppSetting
from app.models.user import User
from app.utils.audit import log_audit_event


router = APIRouter()
logger = logging.getLogger(__name__)

MAX_PROXY_BODY_BYTES = int(os.getenv("GRAFANA_PROXY_MAX_BODY", str(1 * 1024 * 1024)))  # 1 MiB default
PROXY_TIMEOUT = httpx.Timeout(connect=5.0, read=20.0, write=20.0)


def _get_grafana_base(db: Session) -> Optional[str]:
    row = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None), AppSetting.key == "grafana.url")
        .first()
    )
    return (row.value if row else None) or None


def _basic_auth_headers() -> Dict[str, str]:
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
    if (user or os.getenv('GRAFANA_USER', '')) and not user:
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
    base = _get_grafana_base(db)
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

    # Copy incoming headers but drop hop-by-hop and host
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
    headers.setdefault("X-User-Id", str(user.id))
    headers.setdefault("X-Requested-By", "tenantra-backend")

    # Add optional basic auth for upstream Grafana if configured
    headers.update(_basic_auth_headers())

    content_length_header = request.headers.get("content-length")
    if content_length_header:
        try:
            if int(content_length_header) > MAX_PROXY_BODY_BYTES:
                log_audit_event(
                    db,
                    user_id=user.id,
                    action="grafana.proxy",
                    result="denied",
                    ip=client_host,
                    details={
                        "reason": "payload-too-large",
                        "content_length": int(content_length_header),
                        "limit": MAX_PROXY_BODY_BYTES,
                        "path": f"/grafana/{tail}" if tail else "/grafana",
                    },
                )
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Request body exceeds proxy limit")
        except ValueError:
            pass

    body = await request.body()
    if len(body) > MAX_PROXY_BODY_BYTES:
        log_audit_event(
            db,
            user_id=user.id,
            action="grafana.proxy",
            result="denied",
            ip=client_host,
            details={
                "reason": "payload-too-large",
                "content_length": len(body),
                "limit": MAX_PROXY_BODY_BYTES,
                "path": f"/grafana/{tail}" if tail else "/grafana",
            },
        )
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Request body exceeds proxy limit")

    response: Optional[httpx.Response] = None
    status_code: Optional[int] = None
    ok = False
    error_detail: Optional[str] = None
    try:
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT, follow_redirects=False) as client:
            response = await client.request(request.method, upstream, content=body, headers=headers)
        status_code = response.status_code
        ok = 200 <= status_code < 400
        excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
        response_headers = {k: v for k, v in response.headers.items() if k.lower() not in excluded_headers}
        return Response(content=response.content, status_code=status_code, headers=response_headers)
    except httpx.TimeoutException:
        status_code = status.HTTP_504_GATEWAY_TIMEOUT
        error_detail = "Grafana upstream request timed out"
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=error_detail)
    except httpx.HTTPError as exc:
        status_code = status.HTTP_502_BAD_GATEWAY
        error_detail = str(exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=error_detail)
    finally:
        try:
            log_audit_event(
                db,
                user_id=user.id,
                action="grafana.proxy",
                result="success" if ok else "failed",
                ip=client_host,
                details={
                    "method": request.method,
                    "path": f"/grafana/{tail}" if tail else "/grafana",
                    "upstream": upstream,
                    "status": status_code,
                    "tenant_id": user.tenant_id,
                    "bytes": len(body),
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
