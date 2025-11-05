from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.module import Module
from app.models.scheduled_scan import ScheduledScan
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
    # Curated schedules (every 30m, hourly)
    cron_list = ['*/30 * * * *', '0 * * * *']
    for cron in cron_list:
        existing = (
            db.query(ScheduledScan)
            .filter(
                ScheduledScan.tenant_id == tenant_id,
                ScheduledScan.module_id == module.id,
                ScheduledScan.cron_expr == cron,
            )
            .first()
        )
        if existing:
            continue
        schedule = ScheduledScan(
            tenant_id=tenant_id,
            module_id=module.id,
            agent_id=None,
            cron_expr=cron,
            status='scheduled',
            enabled=True,
            next_run_at=compute_next_run(cron),
        )
        db.add(schedule)
        created += 1
    db.commit()
    return {"created": created}

