from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.module import Module
from app.models.scan_job import ScanJob
from app.models.user import User
from app.services.schedule_utils import compute_next_run


router = APIRouter(prefix="/admin/plans", tags=["Admin Plans"])


@router.post("/networking-demo", response_model=Dict[str, int], status_code=status.HTTP_201_CREATED)
def create_networking_demo_plan(
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user),
) -> Dict[str, int]:
    tenant_id = user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="Tenant-scoped user required")

    # Ensure port-scan module exists
    module = db.query(Module).filter(Module.external_id == 'port-scan').first()
    if module is None:
        module = Module(
            external_id='port-scan',
            name='Networking — Port Scan',
            category='Networking',
            phase=1,
            status='active',
            enabled=True,
        )
        db.add(module)
        db.commit(); db.refresh(module)

    created = 0
    cron_list = ['*/30 * * * *', '0 * * * *']
    for cron in cron_list:
        existing = (
            db.query(ScanJob)
            .filter(
                ScanJob.tenant_id == tenant_id,
                ScanJob.module_id == module.id,
                ScanJob.schedule == cron,
                ScanJob.scan_type == "module",
            )
            .first()
        )
        if existing:
            continue
        job = ScanJob(
            tenant_id=tenant_id,
            name=f"{module.name} schedule",
            description="Networking plan preset",
            scan_type="module",
            priority="normal",
            schedule=cron,
            status="scheduled",
            created_by=user.id,
            module_id=module.id,
            agent_id=None,
            parameters=None,
            enabled=True,
            next_run_at=compute_next_run(cron),
        )
        db.add(job)
        created += 1
    db.commit()
    return {"created": created}
