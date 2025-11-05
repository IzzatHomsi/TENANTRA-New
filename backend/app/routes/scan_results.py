import csv
import io
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.agent import Agent
from app.models.file_scan_result import FileScanResult
from app.models.network_scan_result import NetworkScanResult
from app.models.user import User

router = APIRouter(prefix="/scans", tags=["Scan Results"])


def _resolve_tenant(user: User, tenant_id: Optional[int]) -> int:
    if user.tenant_id is not None:
        if tenant_id and tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden tenant scope")
        return user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id required for global administrators")
    return tenant_id


@router.get("/files", response_model=List[Dict[str, object]])
def get_file_results(
    tenant_id: Optional[int] = Query(None, description="Tenant scope (required for global administrators)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> List[Dict[str, object]]:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    rows = (
        db.query(FileScanResult)
        .join(Agent, Agent.id == FileScanResult.agent_id)
        .filter(Agent.tenant_id == resolved_tenant)
        .order_by(FileScanResult.timestamp.desc())
        .limit(200)
        .all()
    )
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "path": r.path,
            "status": r.status,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]


@router.get("/network", response_model=List[Dict[str, object]])
def get_network_results(
    tenant_id: Optional[int] = Query(None, description="Tenant scope (required for global administrators)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> List[Dict[str, object]]:
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    rows = (
        db.query(NetworkScanResult)
        .join(Agent, Agent.id == NetworkScanResult.agent_id)
        .filter(Agent.tenant_id == resolved_tenant)
        .order_by(NetworkScanResult.timestamp.desc())
        .limit(200)
        .all()
    )
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "port": r.port,
            "protocol": r.protocol,
            "status": r.status,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]


@router.get("/files/export.csv")
def export_file_csv(
    tenant_id: Optional[int] = Query(None, description="Tenant scope (required for global administrators)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    rows = (
        db.query(FileScanResult)
        .join(Agent, Agent.id == FileScanResult.agent_id)
        .filter(Agent.tenant_id == resolved_tenant)
        .order_by(FileScanResult.timestamp.desc())
        .limit(200)
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Agent ID", "Path", "Status", "Timestamp"])
    for r in rows:
        writer.writerow([r.agent_id, r.path, r.status, r.timestamp.isoformat()])
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=file_scan_results.csv"})


@router.get("/network/export.csv")
def export_network_csv(
    tenant_id: Optional[int] = Query(None, description="Tenant scope (required for global administrators)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    resolved_tenant = _resolve_tenant(current_user, tenant_id)
    rows = (
        db.query(NetworkScanResult)
        .join(Agent, Agent.id == NetworkScanResult.agent_id)
        .filter(Agent.tenant_id == resolved_tenant)
        .order_by(NetworkScanResult.timestamp.desc())
        .limit(200)
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Agent ID", "Port", "Protocol", "Status", "Timestamp"])
    for r in rows:
        writer.writerow([r.agent_id, r.port, r.protocol, r.status, r.timestamp.isoformat()])
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=network_scan_results.csv"})
