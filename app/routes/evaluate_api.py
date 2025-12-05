from fastapi import APIRouter
from pydantic import BaseModel
from app.services.evaluator import evaluate_summary, semantic_similarity

router = APIRouter()

class EvalRequest(BaseModel):
    generated_summary: str
    reference_summary: str

@router.post("/")
def evaluate(req: EvalRequest):
    rouge_scores = evaluate_summary(req.generated_summary, req.reference_summary)
    semantic = semantic_similarity(req.generated_summary, req.reference_summary)

    return {
        "ROUGE-1": rouge_scores["rouge-1"]["f"],
        "ROUGE-2": rouge_scores["rouge-2"]["f"],
        "ROUGE-L": rouge_scores["rouge-l"]["f"],
        "semantic_similarity": semantic
    }
