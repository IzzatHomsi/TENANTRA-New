from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.compliance_report import ComplianceReportCreate, ComplianceReportInDB
from app.services.compliance_report_service import ComplianceReportService

router = APIRouter()


@router.post("/", response_model=ComplianceReportInDB, status_code=202)
def request_compliance_report(
    report_in: ComplianceReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Request a new compliance report.
    The report generation process will run in the background.
    """
    if report_in.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to request report for this tenant.")

    report_in.generated_by = current_user.id
    compliance_report_service = ComplianceReportService()
    report_job = compliance_report_service.create_report(db, report_in)

    background_tasks.add_task(compliance_report_service.generate_report, db, report_job.id)

    return report_job


@router.get("/{report_id}", response_model=ComplianceReportInDB)
def get_compliance_report_status(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the status of a specific compliance report job.
    """
    compliance_report_service = ComplianceReportService()
    report_job = compliance_report_service.get_report(db, report_id)

    if not report_job:
        raise HTTPException(status_code=404, detail="Compliance report job not found")
    if report_job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this report job.")

    return report_job


@router.get("/", response_model=List[ComplianceReportInDB])
def list_compliance_report_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all compliance report jobs for the current tenant.
    """
    compliance_report_service = ComplianceReportService()
    # In a real app, you'd want pagination and filtering here
    report_jobs = db.query(ComplianceReport).filter(ComplianceReport.tenant_id == current_user.tenant_id).all()
    return report_jobs
