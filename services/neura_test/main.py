"""NeuraTest FastAPI service. Run: uvicorn services.neura_test.main:app --port 8003"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from services.shared.schemas import TestRequest, TestResult, GeneratedFile
from services.neura_test.agent import NeuraTest

app = FastAPI(title="NeuraTest", version="0.1.0")
_agent: NeuraTest | None = None


def get_agent() -> NeuraTest:
    global _agent
    if _agent is None:
        _agent = NeuraTest()
    return _agent


class RunRequest(BaseModel):
    src_files: List[GeneratedFile]
    test_files: List[GeneratedFile]


@app.get("/health")
def health():
    return {"status": "ok", "service": "neura-test"}


@app.post("/generate", response_model=TestResult)
def generate(req: TestRequest):
    try:
        return get_agent().generate_tests(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run", response_model=TestResult)
def run(req: RunRequest):
    try:
        return get_agent().run_tests(req.src_files, req.test_files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
