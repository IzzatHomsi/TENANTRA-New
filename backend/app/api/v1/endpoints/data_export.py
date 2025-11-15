from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.data_export import DataExportJobCreate, DataExportJobInDB
from app.services.data_export_service import DataExportService

router = APIRouter()


@router.post("/", response_model=DataExportJobInDB, status_code=202)
def request_data_export(
    job_in: DataExportJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Request a new data export.
    The export process will run in the background.
    """
    if job_in.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to request export for this tenant.")

    job_in.requested_by = current_user.id
    data_export_service = DataExportService()
    export_job = data_export_service.create_export_job(db, job_in)

    background_tasks.add_task(data_export_service.process_export_job, db, export_job.id)

    return export_job


@router.get("/{job_id}", response_model=DataExportJobInDB)
def get_data_export_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the status of a specific data export job.
    """
    data_export_service = DataExportService()
    export_job = data_export_service.get_export_job(db, job_id)

    if not export_job:
        raise HTTPException(status_code=404, detail="Export job not found")
    if export_job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this export job.")

    return export_job


@router.get("/", response_model=List[DataExportJobInDB])
def list_data_export_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all data export jobs for the current tenant.
    """
    data_export_service = DataExportService()
    # In a real app, you'd want pagination and filtering here
    export_jobs = db.query(DataExportJob).filter(DataExportJob.tenant_id == current_user.tenant_id).all()
    return export_jobs
