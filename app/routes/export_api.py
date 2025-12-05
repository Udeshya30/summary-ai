from fastapi import APIRouter, Response
from app.services.export_pdf import generate_pdf
from app.services.export_excel import generate_excel

router = APIRouter()

@router.post("/pdf")
def export_pdf(data: dict):
    pdf = generate_pdf(
        summary_text=data["summary"],
        findings=data.get("findings", []),
        risk_score=data.get("risk_score", 0),
        exposure=data.get("exposure", 0),
    )

    return Response(
        content=pdf.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=audit_report.pdf"}
    )



@router.post("/excel")
def export_excel(data: dict):
    excel = generate_excel(
        summary=data["summary"],
        findings=data.get("findings", []),
        risk_score=data.get("risk_score", 0),
        exposure=data.get("exposure", 0)
    )

    return Response(
        content=excel.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=audit_report.xlsx"}
    )
