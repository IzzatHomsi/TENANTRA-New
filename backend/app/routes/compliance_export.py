
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.compliance_result import ComplianceResult
import csv
import io
from fpdf import FPDF
from app.core.auth import get_current_user

router = APIRouter(prefix="/compliance", tags=["Compliance Export"])


@router.get("/export.csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    query = (
        db.query(ComplianceResult)
        .order_by(ComplianceResult.recorded_at.desc())
    )
    tenant_id = getattr(current_user, "tenant_id", None)
    if tenant_id is not None:
        query = query.filter(ComplianceResult.tenant_id == tenant_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Module", "Status", "Recorded At"]) 

    rows = query.limit(500).all()
    for r in rows:
        writer.writerow([
            r.id,
            r.module,
            r.status,
            r.recorded_at.isoformat() if r.recorded_at else "",
        ])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=compliance_export.csv"
    return response


@router.get("/export.pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    query = (
        db.query(ComplianceResult)
        .order_by(ComplianceResult.recorded_at.desc())
    )
    tenant_id = getattr(current_user, "tenant_id", None)
    if tenant_id is not None:
        query = query.filter(ComplianceResult.tenant_id == tenant_id)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Compliance Scan Report", ln=True, align="C")
    pdf.ln(10)

    rows = query.limit(100).all()
    for r in rows:
        ts = r.recorded_at.isoformat() if r.recorded_at else ""
        pdf.cell(0, 10, f"{ts} | {r.module} | {r.status}", ln=True)

    output = io.BytesIO()
    pdf.output(output)
    response = Response(content=output.getvalue(), media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=compliance_export.pdf"
    return response
