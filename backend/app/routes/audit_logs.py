"""Audit log API endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


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
        query.order_by(AuditLog.timestamp.desc())
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


def _iter_csv(rows: list[AuditLog]):
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

        yield ",".join(
            [
                esc(
                    r.created_at.isoformat()
                    if isinstance(getattr(r, "created_at", None), datetime)
                    else ""
                ),
                esc(r.user_id),
                esc(r.action),
                esc(r.result),
                esc(getattr(r, "ip", "")),
                esc(getattr(r, "details", "")),
            ]
        ) + "\n"


@router.get("/export")
def export_audit_logs(
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    """Stream CSV export of audit logs with filters."""
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
    query = query.order_by(AuditLog.timestamp.desc())
    rows = query.all()
    return StreamingResponse(
        _iter_csv(rows),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )
