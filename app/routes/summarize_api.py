from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.services.auth_service import current_user
from app.services.pdf_reader import extract_text_from_pdf
from app.services.preprocessor import clean_text
from app.services.report_store import save_report
from app.services.risk_engine import calculate_risk_score, estimate_financial_impact
from app.services.summarizer import generate_summary
from app.services.table_parser import parse_findings

router = APIRouter()
UPLOAD_DIR = Path("data/audit_samples")


@router.post("/pdf")
async def summarize_pdf(file: UploadFile = File(...), user=Depends(current_user)):
    file_name = Path(file.filename or "audit-report.pdf").name
    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF audit reports are supported.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_path = UPLOAD_DIR / f"{uuid4()}-{file_name}"

    with stored_path.open("wb") as f:
        f.write(await file.read())

    raw_text = extract_text_from_pdf(str(stored_path))
    clean = clean_text(raw_text)

    with open("app/prompts/audit_summary.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    summary = generate_summary(clean, prompt)
    findings = parse_findings(summary)
    risk_score = calculate_risk_score(summary)
    financial_impact = estimate_financial_impact(summary)

    return save_report(
        user_id=user["id"],
        file_name=file_name,
        stored_path=str(stored_path),
        summary=summary,
        findings=findings,
        risk_score=risk_score,
        exposure=financial_impact,
        raw_text=clean,
    )
