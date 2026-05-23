from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from app.services.auth_service import current_user
from app.services.report_chat import answer_report_question
from app.services.report_store import (
    add_chat_message,
    delete_report,
    get_report,
    list_reports,
)

router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1200)


@router.get("")
def reports(user=Depends(current_user)):
    return {"reports": list_reports(user["id"])}


@router.get("/{report_id}")
def report_detail(report_id: str, user=Depends(current_user)):
    return get_report(user["id"], report_id)


@router.delete("/{report_id}")
def remove_report(report_id: str, user=Depends(current_user)):
    delete_report(user["id"], report_id)
    return {"message": "Report deleted."}


@router.post("/{report_id}/chat")
def report_chat(report_id: str, req: ChatRequest, user=Depends(current_user)):
    report = get_report(user["id"], report_id)
    user_message = add_chat_message(user["id"], report_id, "user", req.question)
    answer = answer_report_question(report, req.question)
    assistant_message = add_chat_message(user["id"], report_id, "assistant", answer)

    return {
        "answer": answer,
        "messages": [user_message, assistant_message],
    }
