import time
import threading
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple, Optional, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
import os

class RateLimiter:
    def __init__(self, limit: int, window_sec: int):
        self.limit = int(limit)
        self.window = int(window_sec)
        self.buckets: Dict[str, Deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key: str) -> Tuple[bool, int]:
        now = time.time()
        with self.lock:
            q = self.buckets[key]
            while q and (now - q[0]) > self.window:
                q.popleft()
            if len(q) < self.limit:
                q.append(now)
                remaining = self.limit - len(q)
                return True, remaining
            else:
                retry = max(1, int(self.window - (now - q[0])))
                return False, retry

def _parse_routes(spec: str) -> Dict[str, Tuple[int,int]]:
    out = {}
    for part in [p.strip() for p in (spec or '').split(',') if p.strip()]:
        if ':' in part and '/' in part:
            path, lw = part.split(':', 1)
            limit, window = lw.split('/', 1)
            out[path.strip()] = (int(limit), int(window))
    return out

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, default_limit: int = 100, default_window: int = 900, route_overrides: Optional[Dict[str, Tuple[int,int]]] = None, key_func: Optional[Callable[[Request], str]] = None):
        super().__init__(app)
        self.default = RateLimiter(default_limit, default_window)
        self.routes = {path: RateLimiter(l, w) for path, (l, w) in (route_overrides or {}).items()}
        def default_key(req: Request) -> str:
            tenant = req.headers.get('x-tenant-id') or 'global'
            client = req.headers.get('x-forwarded-for', req.client.host if req.client else 'unknown')
            user = req.headers.get('x-user-id') or req.headers.get('x-user-guid') or ''
            return f"{tenant}:{user}:{client}"

        self.key_func = key_func or default_key
        # Always-skipped exact paths
        self.always_skip = {'/health', '/metrics', '/openapi.json', '/docs', '/favicon.ico', '/api/health'}
        # Optional skip prefixes from env (comma-separated). Typical:
        #   RATE_LIMIT_SKIP="/api/auth,/auth,/api/support/settings/public,/support/settings/public"
        raw_skip = os.getenv('RATE_LIMIT_SKIP', '')
        self.skip_prefixes = [p.strip() for p in raw_skip.split(',') if p.strip()]
        # Provide sensible defaults to avoid throttling auth and public settings in dev
        default_skips = [
            '/api/auth', '/auth',
            '/api/health',
            '/api/support/settings/public', '/support/settings/public',
            '/api/scan-orchestration', '/scan-orchestration',
            '/api/admin/observability/grafana', '/grafana',
        ]
        for p in default_skips:
            if p not in self.skip_prefixes:
                self.skip_prefixes.append(p)
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Skip OPTIONS preflight and some readonly endpoints
        if request.method.upper() == 'OPTIONS' or path in self.always_skip:
            return await call_next(request)
        # Skip any configured prefixes
        for pref in self.skip_prefixes:
            if path.startswith(pref):
                return await call_next(request)
        limiter = self.routes.get(path, self.default)
        key = self.key_func(request)
        allowed, aux = limiter.allow(key)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={'detail': 'Too Many Requests'},
                headers={'Retry-After': str(aux), 'X-RateLimit-Limit': str(limiter.limit), 'X-RateLimit-Remaining': '0'}
            )
        resp = await call_next(request)
        try:
            remaining = max(0, aux)
            resp.headers['X-RateLimit-Limit'] = str(limiter.limit)
            resp.headers['X-RateLimit-Remaining'] = str(remaining)
        except Exception:
            pass
        return resp

def build_rate_limit_middleware(app):
    default_l = int(os.getenv('RATE_LIMIT_DEFAULT', '100'))
    default_w = int(os.getenv('RATE_LIMIT_WINDOW', '900'))
    overrides = _parse_routes(os.getenv('RATE_LIMIT_OVERRIDES', ''))
    overrides.setdefault('/api/admin/settings', (20, 60))
    overrides.setdefault('/api/admin/settings/tenant', (20, 60))
    overrides.setdefault('/admin/settings', (20, 60))
    overrides.setdefault('/admin/settings/tenant', (20, 60))
    overrides.setdefault('/admin/observability/grafana/health', (6, 60))
    overrides.setdefault('/api/admin/observability/grafana/health', (6, 60))
    overrides.setdefault('/telemetry/web-vitals', (120, 60))
    overrides.setdefault('/api/telemetry/web-vitals', (120, 60))
    return RateLimitMiddleware(app, default_limit=default_l, default_window=default_w, route_overrides=overrides)
