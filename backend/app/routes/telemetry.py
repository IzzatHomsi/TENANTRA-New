from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.telemetry import WebVitalPayload
from app.observability.metrics import record_web_vital  # type: ignore[attr-defined]

logger = logging.getLogger("tenantra.telemetry")

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post("/web-vitals", status_code=status.HTTP_202_ACCEPTED)
async def ingest_web_vital(
    payload: WebVitalPayload,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    tenant_header = request.headers.get("x-tenant-id")
    user_header = request.headers.get("x-user-id") or request.headers.get("x-user-guid")
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")

    record = {
        "name": payload.name,
        "value": payload.value,
        "rating": (payload.rating or "").lower() or None,
        "navigation_type": payload.navigationType,
        "timestamp": payload.timestamp,
        "tenant": payload.tenant or tenant_header,
        "user_id": payload.userId or user_header,
        "client_ip": client_ip,
        "metric_id": payload.id,
        "url": payload.url,
        "extra": payload.extra,
    }

    # Log for external aggregation and record to metrics collector if available
    logger.info("web_vital", extra={"payload": record})
    try:
        record_web_vital(record)  # type: ignore[call-arg]
    except Exception:
        logger.debug("Unable to record web vital via observability backend.", exc_info=True)

    response.headers.setdefault("Cache-Control", "no-store")
    return {"accepted": True}
