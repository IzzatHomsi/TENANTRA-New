import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

access_log = logging.getLogger("tenantra.access")

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        t0 = time.perf_counter()
        ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "-")
        ua = request.headers.get("user-agent", "-")
        method = request.method
        path = request.url.path
        response = await call_next(request)
        dt_ms = int((time.perf_counter() - t0) * 1000)
        clen = response.headers.get("content-length", "-")
        access_log.info('%s - - "%s %s" %s %s "%s" %dms',
                        ip, method, path, response.status_code, clen, ua, dt_ms)
        return response
