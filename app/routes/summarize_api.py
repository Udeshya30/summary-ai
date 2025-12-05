from fastapi import APIRouter, UploadFile, File
from app.services.pdf_reader import extract_text_from_pdf
from app.services.preprocessor import clean_text
from app.services.summarizer import generate_summary
from app.services.risk_engine import calculate_risk_score, estimate_financial_impact
from app.services.table_parser import parse_findings

router = APIRouter()

@router.post("/pdf")
async def summarize_pdf(file: UploadFile = File(...)):

    # Save uploaded file
    file_path = f"data/audit_samples/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Read + preprocess PDF text
    raw_text = extract_text_from_pdf(file_path)
    clean = clean_text(raw_text)

    # Load summarization prompt
    with open("app/prompts/audit_summary.txt", "r") as f:
        prompt = f.read()

    # Generate structured summary
    summary = generate_summary(clean, prompt)
    findings = parse_findings(summary)

    # 🔥 New Intelligence Layer
    risk_score = calculate_risk_score(summary)
    financial_impact = estimate_financial_impact(summary)

    return {
        "file": file.filename,
        "summary": summary,
        "risk_score_index": risk_score,
        "total_financial_exposure": financial_impact,
        "findings": findings
    }
