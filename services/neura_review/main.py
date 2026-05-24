"""NeuraReview FastAPI service. Run: uvicorn services.neura_review.main:app --port 8005"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from services.shared.schemas import ReviewRequest, ReviewResponse
from services.neura_review.agent import NeuraReview

app = FastAPI(title="NeuraReview", version="0.1.0")
_agent: NeuraReview | None = None


def get_agent() -> NeuraReview:
    global _agent
    if _agent is None:
        _agent = NeuraReview()
    return _agent


@app.get("/health")
def health():
    return {"status": "ok", "service": "neura-review"}


@app.post("/review", response_model=ReviewResponse)
def review(req: ReviewRequest):
    try:
        return get_agent().review(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
