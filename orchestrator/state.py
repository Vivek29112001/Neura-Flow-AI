"""Shared state passed through the LangGraph SDLC pipeline."""
from typing import Optional, TypedDict
from services.shared.schemas import (
    ArchitectResponse,
    BackendResponse,
    FrontendResponse,
    TestResult,
    ReviewResponse,
)


class BuildState(TypedDict, total=False):
    # Input
    feature_spec: str
    target_stack: str
    frontend_framework: str
    constraints: dict
    run_tests: bool
    run_frontend: bool
    run_review: bool

    # Intermediate outputs (filled by each node)
    design: Optional[ArchitectResponse]
    backend: Optional[BackendResponse]
    frontend: Optional[FrontendResponse]
    tests: Optional[TestResult]
    review: Optional[ReviewResponse]

    # Bookkeeping
    error: Optional[str]
