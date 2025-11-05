"""
Compliance reporting API endpoints.

These endpoints provide access to compliance scan results.  The
initial implementation exposes an aggregated trend endpoint that
returns the number of passing and failing scans per day for a
specified time window.  Only authenticated users may query their
tenant's compliance data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.core.auth import get_current_user
from app.models.compliance_result import ComplianceResult
from app.models.user import User


router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.get("/trends")
def compliance_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in the trend"),
    module: Optional[str] = Query(None, description="Filter results by module name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, object]]:
    """Return compliance pass/fail counts per day over a time window.

    The ``days`` parameter specifies how many days back from today to
    include.  Results are filtered to the current user's tenant.  If
    ``module`` is provided, only results for that module are counted.
    The output is a list of objects sorted by date ascending with
    ``date`` (ISO format), ``pass`` and ``fail`` keys.  Days with no
    results are included with zero counts.
    """
    # Determine start timestamp
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)
    # Initialize count dict for each day
    counts = {}
    for i in range(days):
        day = start_date + timedelta(days=i)
        counts[day] = {"pass": 0, "fail": 0}
    # Build base query
    q = db.query(ComplianceResult).filter(
        ComplianceResult.recorded_at >= datetime.combine(start_date, datetime.min.time()),
        ComplianceResult.recorded_at <= datetime.combine(end_date, datetime.max.time()),
    )
    # Filter by tenant
    if current_user.tenant_id is not None:
        q = q.filter(ComplianceResult.tenant_id == current_user.tenant_id)
    # Filter by module
    if module:
        q = q.filter(ComplianceResult.module == module)
    results = q.all()
    # Aggregate counts
    for r in results:
        day = r.recorded_at.date()
        if day in counts:
            if r.status.lower() == "pass":
                counts[day]["pass"] += 1
            else:
                counts[day]["fail"] += 1
    # Convert to list sorted by date
    output = []
    for day in sorted(counts.keys()):
        output.append(
            {
                "date": day.isoformat(),
                "pass": counts[day]["pass"],
                "fail": counts[day]["fail"],
            }
        )
    return output

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

