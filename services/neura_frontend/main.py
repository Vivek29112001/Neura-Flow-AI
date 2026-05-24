"""NeuraFrontend FastAPI service. Run: uvicorn services.neura_frontend.main:app --port 8004"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from services.shared.schemas import FrontendRequest, FrontendResponse
from services.neura_frontend.agent import NeuraFrontend

app = FastAPI(title="NeuraFrontend", version="0.1.0")
_agent: NeuraFrontend | None = None


def get_agent() -> NeuraFrontend:
    global _agent
    if _agent is None:
        _agent = NeuraFrontend()
    return _agent


@app.get("/health")
def health():
    return {"status": "ok", "service": "neura-frontend"}


@app.post("/generate", response_model=FrontendResponse)
def generate(req: FrontendRequest):
    try:
        return get_agent().generate(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
