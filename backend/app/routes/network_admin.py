from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.user import User
from app.services.modules.port_scan import PortScanModule


router = APIRouter(prefix="/admin/network", tags=["Admin Network"])


class PortScanIn(BaseModel):
    host: Optional[str] = Field(None, description="Target host (IP or DNS)")
    ports: Optional[List[int]] = Field(None, description="List of TCP ports to probe")
    targets: Optional[List[Dict[str, object]]] = Field(
        None, description="Optional array of { host, ports[] } objects"
    )
    timeout_ms: Optional[int] = Field(800, ge=100, le=10000)

    @validator("ports", each_item=True)
    def _valid_port(cls, v: int) -> int:  # noqa: N805
        if v <= 0 or v >= 65536:
            raise ValueError("Invalid port number")
        return v

    @validator("targets")
    def _normalize_targets(cls, v):  # noqa: N805
        # Ensure ports are ints and drop invalids to avoid 500s
        try:
            if isinstance(v, list):
                clean = []
                for item in v:
                    if not isinstance(item, dict):
                        continue
                    host = str(item.get("host") or "").strip()
                    ports = item.get("ports") or []
                    if host and isinstance(ports, list):
                        p_int = []
                        for p in ports:
                            try:
                                p = int(p)
                                if 0 < p < 65536:
                                    p_int.append(p)
                            except Exception:
                                continue
                        clean.append({"host": host, "ports": p_int})
                return clean
        except Exception:
            pass
        return v


@router.post("/port-scan", response_model=Dict[str, object])
def run_port_scan(
    payload: PortScanIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
) -> Dict[str, object]:
    params: Dict[str, object] = {}
    if payload.targets:
        params["targets"] = payload.targets
    else:
        if not payload.host:
            raise HTTPException(status_code=400, detail="host or targets[] required")
        params["host"] = payload.host
        params["ports"] = payload.ports or [22, 80, 443]
    if payload.timeout_ms:
        params["timeout_ms"] = payload.timeout_ms

    module = PortScanModule()
    result = module.run(
        type("Ctx", (), {"parameters": params, "module": type("M", (), {"name": module.name, "category": "Networking"})(), "agent_id": None, "tenant_id": None})()
    )
    # Convert ModuleExecutionResult to a plain dict for FastAPI response_model
    return {"status": result.status, "details": result.details, "recorded_at": result.recorded_at.isoformat()}
