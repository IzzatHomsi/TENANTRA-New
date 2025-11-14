"""
Compliance reporting API endpoints.

These endpoints provide access to compliance scan results.  The
initial implementation exposes an aggregated trend endpoint that
returns the number of passing and failing scans per day for a
specified time window.  Only authenticated users may query their
tenant's compliance data.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta, date

from app.database import get_db
from app.core.auth import get_current_user
from app.models.compliance_result import ComplianceResult
from app.models.user import User
from app.schemas.compliance import ComplianceTrendInsights, ComplianceTrendPoint


router = APIRouter(prefix="/compliance", tags=["Compliance"])


def _build_trend_rows(
    *,
    db: Session,
    current_user: User,
    days: int,
    module: Optional[str],
) -> List[Dict[str, object]]:
    end_date: date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)
    buckets = [start_date + timedelta(days=i) for i in range(days)]
    counts: Dict[date, Dict[str, int]] = {bucket: {"pass": 0, "fail": 0} for bucket in buckets}

    query = db.query(ComplianceResult).filter(
        ComplianceResult.recorded_at >= datetime.combine(start_date, datetime.min.time()),
        ComplianceResult.recorded_at <= datetime.combine(end_date, datetime.max.time()),
    )
    if current_user.tenant_id is not None:
        query = query.filter(ComplianceResult.tenant_id == current_user.tenant_id)
    if module:
        query = query.filter(ComplianceResult.module == module)

    results = query.all()
    for row in results:
        recorded_day = row.recorded_at.date()
        bucket = counts.get(recorded_day)
        if not bucket:
            continue
        status = (row.status or "").strip().lower()
        if status == "pass":
            bucket["pass"] += 1
        else:
            bucket["fail"] += 1

    return [
        {
            "date": bucket.isoformat(),
            "pass": counts[bucket]["pass"],
            "fail": counts[bucket]["fail"],
        }
        for bucket in buckets
    ]


@router.get("/trends", response_model=List[ComplianceTrendPoint])
def compliance_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in the trend"),
    module: Optional[str] = Query(None, description="Filter results by module name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, object]]:
    """Return compliance pass/fail counts per day over a time window."""
    return _build_trend_rows(db=db, current_user=current_user, days=days, module=module)


@router.get("/trends/insights", response_model=ComplianceTrendInsights)
def compliance_trend_insights(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in the trend"),
    module: Optional[str] = Query(None, description="Filter results by module name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, object]:
    trend = _build_trend_rows(db=db, current_user=current_user, days=days, module=module)
    total_pass = sum(point["pass"] for point in trend)
    total_fail = sum(point["fail"] for point in trend)
    total = total_pass + total_fail
    coverage = round((total_pass / total) * 100, 2) if total else 0.0

    def _coverage_for_point(point: Dict[str, int]) -> float:
        point_total = point["pass"] + point["fail"]
        if point_total == 0:
            return coverage
        return round((point["pass"] / point_total) * 100, 2)

    first_rate = _coverage_for_point(trend[0]) if trend else coverage
    last_rate = _coverage_for_point(trend[-1]) if trend else coverage
    net_change = round(last_rate - first_rate, 2)

    return {
        "trend": trend,
        "summary": {
            "coverage": coverage,
            "open_failures": total_fail,
            "net_change": net_change,
        },
    }

@router.get("/results")
def list_compliance_results(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    module: Optional[str] = Query(None, description="Filter by module name"),
    status_filter: Optional[str] = Query(None, description="Filter by status (pass/fail)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, object]]:
    query = db.query(ComplianceResult)
    if current_user.tenant_id is not None:
        query = query.filter(ComplianceResult.tenant_id == current_user.tenant_id)
    if module:
        query = query.filter(ComplianceResult.module == module)
    if status_filter:
        query = query.filter(ComplianceResult.status == status_filter)
    rows = (
        query.order_by(ComplianceResult.recorded_at.desc())
        .limit(limit)
        .all()
    )
    results: List[Dict[str, object]] = []
    for row in rows:
        results.append(
            {
                "id": row.id,
                "module": row.module,
                "status": row.status,
                "tenant_id": row.tenant_id,
                "recorded_at": row.recorded_at.isoformat() if row.recorded_at else None,
                "details": row.details,
            }
        )
    return results

