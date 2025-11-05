from __future__ import annotations

import os
from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from urllib.parse import urlparse

from app.core.auth import get_admin_user
from app.database import SessionLocal
from app.models.app_setting import AppSetting
from app.models.user import User


router = APIRouter()


def _get_grafana_base() -> Optional[str]:
    # Read global (tenant_id is NULL) app setting grafana.url
    try:
        db = SessionLocal()
        row = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id.is_(None), AppSetting.key == "grafana.url")
            .first()
        )
        return (row.value if row else None) or None
    except Exception:
        return None
    finally:
        try:
            db.close()
        except Exception:
            pass


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


async def _proxy(request: Request, tail: str) -> Response:
    base = _get_grafana_base()
    if not base:
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

    # Add optional basic auth for upstream Grafana if configured
    headers.update(_basic_auth_headers())

    timeout = httpx.Timeout(connect=10.0, read=60.0, write=60.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        # Prepare request content/stream
        body = await request.body()
        resp = await client.request(request.method, upstream, content=body, headers=headers)

    # Build streaming response with upstream headers and status
    excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
    response_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded_headers]
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(response_headers))


@router.api_route("/grafana", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def grafana_root(
    request: Request,
    _current_user: User = Depends(get_admin_user),
) -> Response:
    return await _proxy(request, tail="")


@router.api_route("/grafana/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def grafana_any(
    path: str,
    request: Request,
    _current_user: User = Depends(get_admin_user),
) -> Response:
    return await _proxy(request, tail=path)
