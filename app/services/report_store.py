import json
from uuid import uuid4

from fastapi import HTTPException

from app.database import get_connection
from app.services.auth_service import iso_now


def save_report(user_id, file_name, stored_path, summary, findings, risk_score, exposure, raw_text):
    report_id = str(uuid4())
    created_at = iso_now()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO audit_reports (
                id, user_id, file_name, stored_path, summary, findings_json,
                risk_score, exposure, raw_text, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                user_id,
                file_name,
                stored_path,
                summary,
                json.dumps(findings),
                int(risk_score or 0),
                float(exposure or 0),
                raw_text,
                created_at,
            ),
        )

    return get_report(user_id, report_id)


def list_reports(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, file_name, summary, findings_json, risk_score, exposure, created_at
            FROM audit_reports
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()

    return [report_summary(row) for row in rows]


def get_report(user_id, report_id):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, file_name, stored_path, summary, findings_json,
                   risk_score, exposure, raw_text, created_at
            FROM audit_reports
            WHERE user_id = ? AND id = ?
            """,
            (user_id, report_id),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found.")

    return hydrate_report(row)


def delete_report(user_id, report_id):
    with get_connection() as conn:
        result = conn.execute(
            "DELETE FROM audit_reports WHERE user_id = ? AND id = ?",
            (user_id, report_id),
        )

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Report not found.")


def add_chat_message(user_id, report_id, role, message):
    message_id = str(uuid4())
    created_at = iso_now()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO report_chats (id, report_id, user_id, role, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (message_id, report_id, user_id, role, message, created_at),
        )

    return {
        "id": message_id,
        "role": role,
        "message": message,
        "created_at": created_at,
    }


def list_chat_messages(user_id, report_id):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, role, message, created_at
            FROM report_chats
            WHERE user_id = ? AND report_id = ?
            ORDER BY created_at ASC
            """,
            (user_id, report_id),
        ).fetchall()

    return [dict(row) for row in rows]


def hydrate_report(row):
    findings = parse_findings_json(row["findings_json"])
    return {
        "id": row["id"],
        "file": row["file_name"],
        "file_name": row["file_name"],
        "summary": row["summary"],
        "findings": findings,
        "risk_score_index": row["risk_score"],
        "total_financial_exposure": row["exposure"],
        "created_at": row["created_at"],
        "chat_messages": list_chat_messages(row["user_id"], row["id"]),
    }


def report_summary(row):
    findings = parse_findings_json(row["findings_json"])
    summary = row["summary"] or ""
    return {
        "id": row["id"],
        "file_name": row["file_name"],
        "summary_preview": summary[:220],
        "findings_count": len(findings),
        "risk_score_index": row["risk_score"],
        "total_financial_exposure": row["exposure"],
        "created_at": row["created_at"],
    }


def parse_findings_json(value):
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []
