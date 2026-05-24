"""
Shared Pydantic schemas — the contract between SDLC agent services.
Keep these stable; agents are coupled via these shapes, not internals.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# ---------- NeuraArchitect ----------

class ArchitectRequest(BaseModel):
    feature_spec: str = Field(..., description="Natural-language description of what to build")
    constraints: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional non-functional constraints",
    )
    target_stack: Optional[str] = Field(
        default="FastAPI + SQLAlchemy + Postgres",
        description="Preferred stack (used as a hint, not a hard constraint)",
    )


class APIEndpoint(BaseModel):
    method: str
    path: str
    summary: str
    request_body: Optional[Dict] = None
    response_body: Optional[Dict] = None


class DBTable(BaseModel):
    name: str
    columns: List[Dict[str, str]]


class ArchitectResponse(BaseModel):
    summary: str
    stack: str
    endpoints: List[APIEndpoint]
    db_schema: List[DBTable]
    rationale: str


# ---------- NeuraBackend ----------

class BackendRequest(BaseModel):
    design: ArchitectResponse


class GeneratedFile(BaseModel):
    path: str
    content: str
    language: str = "python"


class BackendResponse(BaseModel):
    files: List[GeneratedFile]
    install_commands: List[str] = []
    notes: Optional[str] = None


# ---------- NeuraTest ----------

class TestRequest(BaseModel):
    files: List[GeneratedFile]
    design: Optional[ArchitectResponse] = None


class TestResult(BaseModel):
    test_files: List[GeneratedFile]
    coverage_estimate: Optional[float] = None
    notes: Optional[str] = None
    executed: bool = False
    passed: Optional[int] = None
    failed: Optional[int] = None
    output: Optional[str] = None


# ---------- NeuraFrontend ----------

class FrontendRequest(BaseModel):
    design: ArchitectResponse
    framework: Optional[str] = "Next.js 14 App Router + Tailwind"
    api_base_url: Optional[str] = "http://localhost:8000"


class FrontendResponse(BaseModel):
    files: List[GeneratedFile]
    install_commands: List[str] = []
    notes: Optional[str] = None


# ---------- NeuraReview ----------

class ReviewIssue(BaseModel):
    severity: str
    category: str
    file: Optional[str] = None
    line: Optional[int] = None
    message: str
    suggestion: Optional[str] = None


class ReviewRequest(BaseModel):
    design: Optional[ArchitectResponse] = None
    backend: Optional[BackendResponse] = None
    frontend: Optional[FrontendResponse] = None
    tests: Optional[TestResult] = None


class ReviewResponse(BaseModel):
    issues: List[ReviewIssue]
    summary: str
    overall_status: str


# ---------- Orchestrator ----------

class BuildRequest(BaseModel):
    feature_spec: str
    constraints: Optional[Dict[str, str]] = None
    target_stack: Optional[str] = "FastAPI + SQLAlchemy + Postgres"
    frontend_framework: Optional[str] = "Next.js 14 App Router + Tailwind"
    run_tests: bool = True
    run_frontend: bool = True
    run_review: bool = True


class BuildResponse(BaseModel):
    design: ArchitectResponse
    backend: BackendResponse
    frontend: Optional[FrontendResponse] = None
    tests: Optional[TestResult] = None
    review: Optional[ReviewResponse] = None
    status: str = "ok"
