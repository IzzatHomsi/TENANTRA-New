import uuid
import logging
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging_conf import set_request_context
from app.core.security import decode_access_token

log = logging.getLogger("tenantra.request")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = uuid.uuid4().hex[:12]
        user_id = None
        # Try to read user id from Bearer token
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
            try:
                payload = decode_access_token(token)
                if payload and "sub" in payload:
                    user_id = payload["sub"]
            except Exception:
                pass

        set_request_context(request_id=req_id, user_id=user_id, path=request.url.path, method=request.method, status=None)
        started = datetime.utcnow()

        try:
            response = await call_next(request)
            set_request_context(status=str(response.status_code))
            log.info("REQ %s %s -> %s in %dms", request.method, request.url.path, response.status_code, int((datetime.utcnow()-started).total_seconds()*1000))
            return response
        except Exception as ex:
            set_request_context(status="500")
            log.exception("Unhandled error for %s %s: %s", request.method, request.url.path, ex)
            raise
