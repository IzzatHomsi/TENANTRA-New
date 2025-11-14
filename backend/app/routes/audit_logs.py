"""Audit log API endpoints."""

import os
import time
import threading
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

_EXPORT_MAX = int(os.getenv("AUDIT_EXPORT_MAX_PER_MINUTE", "6"))
_EXPORT_WINDOW = int(os.getenv("AUDIT_EXPORT_WINDOW_SECONDS", "60"))
_EXPORT_LOCK = threading.Lock()
_EXPORT_BUCKETS: Dict[int, Deque[float]] = {}


def _enforce_export_rate_limit(user: User) -> None:
    if _EXPORT_MAX <= 0:
        return
    now = time.monotonic()
    key = int(getattr(user, "id", 0) or 0)
    with _EXPORT_LOCK:
        bucket = _EXPORT_BUCKETS.setdefault(key, deque())
        while bucket and now - bucket[0] > _EXPORT_WINDOW:
            bucket.popleft()
        if len(bucket) >= _EXPORT_MAX:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many audit exports requested. Try again shortly.",
            )
        bucket.append(now)


def _serialize_audit_log(log: AuditLog) -> Dict[str, Any]:
    data = log.as_dict()
    created_at = data.get("created_at")
    if isinstance(created_at, datetime):
        iso = created_at.isoformat()
        data["created_at"] = iso
        data.setdefault("timestamp", iso)
    updated_at = data.get("updated_at")
    if isinstance(updated_at, datetime):
        data["updated_at"] = updated_at.isoformat()
    try:
        data["details"] = log.details
    except Exception:
        data["details"] = None
    return data


@router.get("")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) inclusive"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) inclusive"),
    result: Optional[str] = Query(None, description="Filter by result (success, failure, denied)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Number of records per page"),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    """Retrieve audit logs with optional filtering and pagination."""
    query = db.query(AuditLog)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    try:
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(AuditLog.created_at >= start_dt)
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(AuditLog.created_at <= end_dt)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD")
    if result:
        query = query.filter(AuditLog.result == result)
    total = query.count()
    logs: List[AuditLog] = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_serialize_audit_log(log) for log in logs],
    }


def _iter_csv(rows: List[Dict[str, Any]]):
    # CSV header
    header = ["timestamp", "user_id", "action", "result", "ip", "details"]
    yield ",".join(header) + "\n"
    for r in rows:
        # Basic, safe CSV escaping for double-quotes
        def esc(v: object) -> str:
            s = "" if v is None else str(v)
            s = s.replace("\r", " ").replace("\n", " ")
            s = s.replace('"', '""')
            return f'"{s}"'

        details_value = r.get("details", "")
        yield ",".join(
            [
                esc(
                    r.get("created_at")
                    if isinstance(r.get("created_at"), str)
                    else r.get("timestamp", "")
                ),
                esc(r.get("user_id")),
                esc(r.get("action")),
                esc(r.get("result")),
                esc(r.get("ip", "")),
                esc(details_value),
            ]
        ) + "\n"


@router.get("/export")
def export_audit_logs(
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Stream CSV export of audit logs with filters."""
    _enforce_export_rate_limit(current_user)
    query = db.query(AuditLog)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    try:
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(AuditLog.created_at >= start_dt)
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(AuditLog.created_at <= end_dt)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD")
    if result:
        query = query.filter(AuditLog.result == result)
    query = query.order_by(AuditLog.created_at.desc())
    rows = query.all()
    row_dicts = [_serialize_audit_log(row) for row in rows]
    try:
        log_audit_event(
            db,
            user_id=current_user.id,
            action="audit_logs.export",
            result="success",
            ip=None,
            details={
                "filters": {
                    "user_id": user_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "result": result,
                },
                "row_count": len(row_dicts),
            },
        )
    except Exception:
        pass
    return StreamingResponse(
        _iter_csv(row_dicts),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )
