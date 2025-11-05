
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.compliance_result import ComplianceResult
import csv
import io
from fpdf import FPDF

router = APIRouter(prefix="/compliance", tags=["Compliance Export"])


@router.get("/export.csv")
def export_csv(db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Module", "Status", "Recorded At"]) 

    rows = (
        db.query(ComplianceResult)
        .order_by(ComplianceResult.recorded_at.desc())
        .limit(500)
        .all()
    )
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
def export_pdf(db: Session = Depends(get_db)):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Compliance Scan Report", ln=True, align="C")
    pdf.ln(10)

    rows = (
        db.query(ComplianceResult)
        .order_by(ComplianceResult.recorded_at.desc())
        .limit(100)
        .all()
    )
    for r in rows:
        ts = r.recorded_at.isoformat() if r.recorded_at else ""
        pdf.cell(0, 10, f"{ts} | {r.module} | {r.status}", ln=True)

    output = io.BytesIO()
    pdf.output(output)
    response = Response(content=output.getvalue(), media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=compliance_export.pdf"
    return response
