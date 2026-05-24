"""NeuraBackend FastAPI service. Run: uvicorn services.neura_backend.main:app --port 8002"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from services.shared.schemas import BackendRequest, BackendResponse
from services.neura_backend.agent import NeuraBackend

app = FastAPI(title="NeuraBackend", version="0.1.0")
_agent: NeuraBackend | None = None


def get_agent() -> NeuraBackend:
    global _agent
    if _agent is None:
        _agent = NeuraBackend()
    return _agent


@app.get("/health")
def health():
    return {"status": "ok", "service": "neura-backend"}


@app.post("/generate", response_model=BackendResponse)
def generate(req: BackendRequest):
    try:
        return get_agent().generate(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
