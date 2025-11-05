"""Module execution endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.module import Module
from app.models.scan_module_result import ScanModuleResult
from app.models.user import User
from app.schemas.module_runs import ModuleRunRequest, ModuleRunResponse
from app.services.module_executor import ModuleRunnerNotFound, execute_module
from app.services.module_runner import ModuleExecutionError

router = APIRouter(prefix="/module-runs", tags=["Module Runs"])


def _get_module_or_404(db: Session, module_id: int) -> Module:
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return module


@router.post("/{module_id}", response_model=ModuleRunResponse, status_code=status.HTTP_201_CREATED)
def run_module(
    module_id: int,
    payload: ModuleRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> ModuleRunResponse:
    module = _get_module_or_404(db, module_id)
    try:
        record = execute_module(
            db=db,
            module=module,
            tenant_id=current_user.tenant_id,
            agent_id=payload.agent_id,
            user_id=current_user.id,
            parameters=payload.parameters or {},
        )
    except ModuleRunnerNotFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Module does not have an executable implementation yet")
    except ModuleExecutionError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return ModuleRunResponse.from_orm(record)


@router.get("", response_model=List[ModuleRunResponse])
def list_runs(
    module_id: Optional[int] = Query(None, description="Filter by module"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> List[ModuleRunResponse]:
    query = db.query(ScanModuleResult).filter(ScanModuleResult.tenant_id == current_user.tenant_id)
    if module_id is not None:
        query = query.filter(ScanModuleResult.module_id == module_id)
    rows = query.order_by(ScanModuleResult.recorded_at.desc()).limit(limit).all()
    return [ModuleRunResponse.from_orm(row) for row in rows]
