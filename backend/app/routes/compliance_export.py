
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.compliance_result import ComplianceResult
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.dependencies.tenancy import tenant_scope_dependency

router = APIRouter(prefix="/compliance", tags=["Compliance Export"])


@router.get("/export.csv")
def export_csv(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(tenant_scope_dependency()),
):
    query = (
        db.query(ComplianceResult)
        .order_by(ComplianceResult.recorded_at.desc())
    )
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
    tenant_id: int = Depends(tenant_scope_dependency()),
):
    query = (
        db.query(ComplianceResult)
        .order_by(ComplianceResult.recorded_at.desc())
    )
    query = query.filter(ComplianceResult.tenant_id == tenant_id)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, y, "Compliance Scan Report")
    y -= 24
    pdf.setFont("Helvetica", 10)
    rows = query.limit(100).all()
    for r in rows:
        ts = r.recorded_at.isoformat() if r.recorded_at else ""
        pdf.drawString(40, y, f"{ts} | {r.module} | {r.status}")
        y -= 14
        if y < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - 40

    pdf.save()
    buffer.seek(0)
    response = Response(content=buffer.read(), media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=compliance_export.pdf"
    return response
