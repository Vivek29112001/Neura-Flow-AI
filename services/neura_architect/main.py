"""NeuraArchitect FastAPI service. Run: uvicorn services.neura_architect.main:app --port 8001"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from services.shared.schemas import ArchitectRequest, ArchitectResponse
from services.neura_architect.agent import NeuraArchitect

app = FastAPI(title="NeuraArchitect", version="0.1.0")
_agent: NeuraArchitect | None = None


def get_agent() -> NeuraArchitect:
    global _agent
    if _agent is None:
        _agent = NeuraArchitect()
    return _agent


@app.get("/health")
def health():
    return {"status": "ok", "service": "neura-architect"}


@app.post("/design", response_model=ArchitectResponse)
def design(req: ArchitectRequest):
    try:
        return get_agent().design(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
