"""
NeuraTest — generates pytest tests for backend code, then optionally
executes them in an isolated temp directory and parses results.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from services.shared.llm_client import NeuraLLM
from services.shared.rag import NeuraRAG
from services.shared.schemas import (
    TestRequest,
    TestResult,
    GeneratedFile,
)


SYSTEM_PROMPT = """You are NeuraTest, the QA agent in Neura-flow AI.

You receive generated backend code and produce pytest tests as JSON:
{
  "test_files": [
    {"path":"tests/test_x.py","content":"<full pytest file>","language":"python"}
  ],
  "coverage_estimate": 0.78,
  "notes": "<which paths are not yet covered>"
}

Rules:
- Output valid JSON only.
- Cover every endpoint and major code path.
- Use FastAPI's TestClient for HTTP routes; use pytest fixtures for DB setup.
- Make tests fast and hermetic — no external HTTP, no real DB unless sqlite-in-memory.
- Realistic assertions, not just status==200.
"""


class NeuraTest:
    def __init__(self):
        self.llm = NeuraLLM()
        self.rag = NeuraRAG(collection="test")

    def generate_tests(self, req: TestRequest) -> TestResult:
        # Concatenate source files into a single prompt block (truncated if huge)
        src_block = "\n\n".join(
            f"### FILE: {f.path}\n```{f.language}\n{f.content[:6000]}\n```"
            for f in req.files
        )
        design_block = ""
        if req.design:
            design_block = f"\nDESIGN:\n{req.design.model_dump_json(indent=2)}\n"

        context = self.rag.context_block(src_block[:1000], k=3)

        user_prompt = (
            (f"{context}\n\n" if context else "")
            + design_block
            + f"\nSOURCE FILES:\n{src_block}\n\n"
            + "Return the JSON of test files now."
        )
        raw = self.llm.json_chat(SYSTEM_PROMPT, user_prompt, max_tokens=8192)
        data = json.loads(raw)

        test_files = [GeneratedFile(**f) for f in data.get("test_files", [])]

        result = TestResult(
            test_files=test_files,
            coverage_estimate=data.get("coverage_estimate"),
            notes=data.get("notes"),
        )

        self.rag.add(
            documents=[
                f"Tests generated for {len(req.files)} files. "
                f"Test count: {len(test_files)}. Notes: {result.notes or ''}"
            ],
            metadatas=[{"type": "test_gen"}],
        )
        return result

    def run_tests(self, src_files: List[GeneratedFile], test_files: List[GeneratedFile]) -> TestResult:
        """
        Write all files to a temp dir, run pytest, parse the result.
        Returns a TestResult populated with executed/passed/failed/output.
        """
        with tempfile.TemporaryDirectory(prefix="neuratest_") as tmp:
            tmp_path = Path(tmp)
            for f in list(src_files) + list(test_files):
                fp = tmp_path / f.path
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text(f.content, encoding="utf-8")

            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", "--tb=short"],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                output = proc.stdout + "\n" + proc.stderr
            except subprocess.TimeoutExpired:
                output = "TIMEOUT: pytest exceeded 120s"

        passed, failed = self._parse_pytest_summary(output)
        return TestResult(
            test_files=test_files,
            executed=True,
            passed=passed,
            failed=failed,
            output=output[-4000:],  # cap output for transport
        )

    @staticmethod
    def _parse_pytest_summary(output: str):
        """Extract passed/failed counts from pytest's summary line."""
        passed = failed = 0
        m_p = re.search(r"(\d+)\s+passed", output)
        m_f = re.search(r"(\d+)\s+failed", output)
        if m_p:
            passed = int(m_p.group(1))
        if m_f:
            failed = int(m_f.group(1))
        return passed, failed
