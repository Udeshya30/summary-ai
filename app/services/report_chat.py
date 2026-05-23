import os

from fastapi import HTTPException
from openai import OpenAI


def answer_report_question(report, question):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Chatbot is not configured. Add OPENAI_API_KEY to enable report chat.")

    client = OpenAI(api_key=api_key)
    context = build_context(report)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an internal audit assistant. Answer only from the provided report context. "
                    "If the answer is not in the report, say that the report does not provide enough information. "
                    "Keep answers concise, factual, and suitable for audit review."
                ),
            },
            {
                "role": "user",
                "content": f"Report context:\n{context}\n\nQuestion: {question}",
            },
        ],
        max_tokens=450,
        temperature=0.1,
    )

    return response.choices[0].message.content


def build_context(report):
    findings = "\n".join(
        [
            f"- Issue: {item.get('issue', 'Not specified')}; Risk: {item.get('risk', 'Not specified')}; "
            f"Impact: {item.get('impact', 'Not specified')}; Root cause: {item.get('root_cause', 'Not specified')}"
            for item in report.get("findings", [])
        ]
    )

    return (
        f"File: {report.get('file_name') or report.get('file')}\n"
        f"Risk score: {report.get('risk_score_index')}\n"
        f"Total exposure: {report.get('total_financial_exposure')}\n\n"
        f"Summary:\n{report.get('summary', '')}\n\n"
        f"Findings:\n{findings or 'No structured findings.'}"
    )
