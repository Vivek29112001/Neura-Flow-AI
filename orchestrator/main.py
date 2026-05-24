"""
NeuraBuild orchestrator — the front door for Phase 2.

POST /build with a feature spec. The orchestrator drives the LangGraph
state machine, which fans out to NeuraArchitect, NeuraBackend, NeuraFrontend,
NeuraTest, and NeuraReview services and returns the consolidated build result.

Run: uvicorn orchestrator.main:app --port 8000
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from services.shared.schemas import BuildRequest, BuildResponse
from orchestrator.graph import GRAPH

app = FastAPI(title="NeuraBuild Orchestrator", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "neura-build-orchestrator"}


@app.post("/build", response_model=BuildResponse)
def build(req: BuildRequest):
    try:
        final_state = GRAPH.invoke(
            {
                "feature_spec": req.feature_spec,
                "target_stack": req.target_stack or "FastAPI + SQLAlchemy + Postgres",
                "frontend_framework": req.frontend_framework or "Next.js 14 App Router + Tailwind",
                "constraints": req.constraints or {},
                "run_tests": req.run_tests,
                "run_frontend": req.run_frontend,
                "run_review": req.run_review,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"graph failed: {e}")

    if final_state.get("error"):
        raise HTTPException(status_code=500, detail=final_state["error"])

    return BuildResponse(
        design=final_state["design"],
        backend=final_state["backend"],
        frontend=final_state.get("frontend"),
        tests=final_state.get("tests"),
        review=final_state.get("review"),
        status="ok",
    )
