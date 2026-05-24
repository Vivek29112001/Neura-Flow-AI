"""
LangGraph state machine for the SDLC pipeline.

Flow (default — all branches enabled):

                ┌──→ frontend ─────────────────────────────┐
   START → architect                                       ├→ review → END
                └──→ backend ──→ test_gen ──→ test_run ────┘
                       │
                       └─── (run_tests=false) ──────────────↑

Frontend and backend run in PARALLEL after architect — LangGraph fans out
on multiple outgoing edges, then synchronizes when their downstream
edges converge on `review`.

Each node calls the corresponding microservice over HTTP, keeping the
orchestrator thin and the agents independently deployable.
"""
import os
import sys
from pathlib import Path
from typing import Literal

import httpx
from langgraph.graph import StateGraph, START, END

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.shared.schemas import (
    ArchitectRequest,
    ArchitectResponse,
    BackendRequest,
    BackendResponse,
    FrontendRequest,
    FrontendResponse,
    TestRequest,
    TestResult,
    ReviewRequest,
    ReviewResponse,
)
from orchestrator.state import BuildState


# Service URLs — override via env when deployed
ARCHITECT_URL = os.getenv("NEURA_ARCHITECT_URL", "http://localhost:8001")
BACKEND_URL = os.getenv("NEURA_BACKEND_URL", "http://localhost:8002")
TEST_URL = os.getenv("NEURA_TEST_URL", "http://localhost:8003")
FRONTEND_URL = os.getenv("NEURA_FRONTEND_URL", "http://localhost:8004")
REVIEW_URL = os.getenv("NEURA_REVIEW_URL", "http://localhost:8005")

# Single shared client — keeps connections warm
_client = httpx.Client(timeout=300.0)


def _node_architect(state: BuildState) -> BuildState:
    req = ArchitectRequest(
        feature_spec=state["feature_spec"],
        target_stack=state.get("target_stack", "FastAPI + SQLAlchemy + Postgres"),
        constraints=state.get("constraints"),
    )
    r = _client.post(f"{ARCHITECT_URL}/design", json=req.model_dump())
    r.raise_for_status()
    return {"design": ArchitectResponse(**r.json())}


def _node_backend(state: BuildState) -> BuildState:
    design = state.get("design")
    if design is None:
        return {"error": "no design produced"}
    req = BackendRequest(design=design)
    r = _client.post(f"{BACKEND_URL}/generate", json=req.model_dump())
    r.raise_for_status()
    return {"backend": BackendResponse(**r.json())}


def _node_frontend(state: BuildState) -> BuildState:
    design = state.get("design")
    if design is None:
        return {"error": "no design produced"}
    req = FrontendRequest(
        design=design,
        framework=state.get("frontend_framework", "Next.js 14 App Router + Tailwind"),
    )
    r = _client.post(f"{FRONTEND_URL}/generate", json=req.model_dump())
    r.raise_for_status()
    return {"frontend": FrontendResponse(**r.json())}


def _node_test_gen(state: BuildState) -> BuildState:
    backend = state.get("backend")
    if backend is None:
        return {"error": "no backend produced"}
    req = TestRequest(files=backend.files, design=state.get("design"))
    r = _client.post(f"{TEST_URL}/generate", json=req.model_dump())
    r.raise_for_status()
    return {"tests": TestResult(**r.json())}


def _node_test_run(state: BuildState) -> BuildState:
    backend = state.get("backend")
    tests = state.get("tests")
    if backend is None or tests is None:
        return {"error": "missing backend or tests"}
    payload = {
        "src_files": [f.model_dump() for f in backend.files],
        "test_files": [f.model_dump() for f in tests.test_files],
    }
    r = _client.post(f"{TEST_URL}/run", json=payload)
    r.raise_for_status()
    return {"tests": TestResult(**r.json())}


def _node_review(state: BuildState) -> BuildState:
    if not state.get("run_review", True):
        return {}
    req = ReviewRequest(
        design=state.get("design"),
        backend=state.get("backend"),
        frontend=state.get("frontend"),
        tests=state.get("tests"),
    )
    r = _client.post(f"{REVIEW_URL}/review", json=req.model_dump())
    r.raise_for_status()
    return {"review": ReviewResponse(**r.json())}


# ---- Conditional routers ----

def _after_backend(state: BuildState) -> Literal["test_gen", "review"]:
    """If tests are disabled, skip directly to the review join."""
    return "test_gen" if state.get("run_tests", True) else "review"


# ---- Graph construction ----

def build_graph():
    g = StateGraph(BuildState)
    g.add_node("architect", _node_architect)
    g.add_node("frontend", _node_frontend)
    g.add_node("backend", _node_backend)
    g.add_node("test_gen", _node_test_gen)
    g.add_node("test_run", _node_test_run)
    g.add_node("review", _node_review)

    # Fan-out: architect kicks off both frontend and backend in parallel
    g.add_edge(START, "architect")
    g.add_edge("architect", "frontend")
    g.add_edge("architect", "backend")

    # Backend optionally runs tests
    g.add_conditional_edges(
        "backend",
        _after_backend,
        {"test_gen": "test_gen", "review": "review"},
    )
    g.add_edge("test_gen", "test_run")

    # Fan-in: review waits for frontend AND (test_run OR backend->review)
    g.add_edge("frontend", "review")
    g.add_edge("test_run", "review")

    g.add_edge("review", END)

    return g.compile()


# Module-level compiled graph — reused across requests
GRAPH = build_graph()
