import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

HEADER = "X-Request-ID"

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get(HEADER) or str(uuid.uuid4())
        # make request id available to handlers via state
        request.state.request_id = rid
        response = await call_next(request)
        response.headers.setdefault(HEADER, rid)
        return response
