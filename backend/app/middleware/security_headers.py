from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request
import os

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.hsts = os.getenv("SEC_HSTS", "max-age=63072000; includeSubDomains; preload")
        self.frame = os.getenv("SEC_FRAME_OPTIONS", "DENY")
        self.cto = os.getenv("SEC_CONTENT_TYPE_OPTIONS", "nosniff")
        self.referrer = os.getenv("SEC_REFERRER_POLICY", "no-referrer")
        self.coop = os.getenv("SEC_COOP", "same-origin")
        self.coep = os.getenv("SEC_COEP", "require-corp")
        self.csp = os.getenv(
            "SEC_CSP",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        )

    async def dispatch(self, request: Request, call_next):
        resp = await call_next(request)
        path = request.url.path or ""
        # For proxied Grafana paths, avoid setting restrictive headers
        is_grafana = path.startswith("/grafana")
        if request.url.scheme == "https" or os.getenv("SEC_FORCE_HSTS", "false").lower() in ("1","true","yes"):
            resp.headers.setdefault("Strict-Transport-Security", self.hsts)
        if not is_grafana:
            resp.headers.setdefault("X-Frame-Options", self.frame)
        resp.headers.setdefault("X-Content-Type-Options", self.cto)
        resp.headers.setdefault("Referrer-Policy", self.referrer)
        if not is_grafana:
            resp.headers.setdefault("Cross-Origin-Opener-Policy", self.coop)
            resp.headers.setdefault("Cross-Origin-Embedder-Policy", self.coep)
            resp.headers.setdefault("Content-Security-Policy", self.csp)
        return resp
