"""
NeuraReview — final quality gate.

Consumes the design + generated backend + frontend + test results, runs
a senior-engineer style review, and returns a list of categorized issues
plus an overall_status ('approved' | 'changes_requested' | 'blocked').

Categories: security, performance, style, bug, design, coverage.
Severities: critical, high, medium, low, info.

This agent does NOT execute code — it reviews. The pytest pass/fail counts
from NeuraTest already provide the runtime signal.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from services.shared.llm_client import NeuraLLM
from services.shared.rag import NeuraRAG
from services.shared.schemas import (
    ReviewRequest,
    ReviewResponse,
    ReviewIssue,
)


SYSTEM_PROMPT = """You are NeuraReview, the senior code reviewer in Neura-flow AI.

You receive design + backend code + frontend code + test results, and produce
a structured review as JSON:
{
  "issues": [
    {
      "severity": "critical|high|medium|low|info",
      "category": "security|performance|style|bug|design|coverage",
      "file": "app/main.py",
      "line": 42,
      "message": "<what's wrong>",
      "suggestion": "<concrete fix>"
    }
  ],
  "summary": "<2-4 sentence overall verdict>",
  "overall_status": "approved | changes_requested | blocked"
}

Status rules:
- 'blocked'             — any critical issue (security, data-loss, crash, broken endpoint), or all tests failed.
- 'changes_requested'   — any high issue, or design/code mismatch, or significant coverage gap.
- 'approved'            — only medium/low/info issues remain.

Review rules:
- Be specific. 'Improve error handling' is useless; cite the file/line and the missing case.
- Cross-check design vs implementation: did every endpoint in design.endpoints land in the backend?
- Check frontend ↔ backend contract: do the API client calls match endpoint paths and bodies?
- If tests were executed and failed.count > 0, every failure must produce at least one issue.
- Don't invent files or lines. If you didn't see the file, don't cite it.
- Output JSON only.
"""


class NeuraReview:
    def __init__(self):
        self.llm = NeuraLLM()
        self.rag = NeuraRAG(collection="review")

    def review(self, req: ReviewRequest) -> ReviewResponse:
        # Build a single review packet. Cap file contents so prompt stays sane.
        parts = []
        if req.design is not None:
            parts.append(f"DESIGN:\n{req.design.model_dump_json(indent=2)}")

        if req.backend is not None:
            parts.append("BACKEND FILES:")
            for f in req.backend.files:
                parts.append(f"### {f.path}\n```{f.language}\n{f.content[:4000]}\n```")

        if req.frontend is not None:
            parts.append("FRONTEND FILES:")
            for f in req.frontend.files:
                parts.append(f"### {f.path}\n```{f.language}\n{f.content[:4000]}\n```")

        if req.tests is not None:
            t = req.tests
            parts.append(
                f"TEST RESULTS:\n"
                f"executed={t.executed} passed={t.passed} failed={t.failed} "
                f"coverage_estimate={t.coverage_estimate}\n"
                f"notes: {t.notes or ''}\n"
                f"output_tail:\n{(t.output or '')[-2000:]}"
            )

        review_input = "\n\n".join(parts)
        context = self.rag.context_block(review_input[:1000], k=3)

        user_prompt = (
            (f"{context}\n\n" if context else "")
            + f"{review_input}\n\n"
            + "Now produce the review JSON."
        )
        raw = self.llm.json_chat(SYSTEM_PROMPT, user_prompt, max_tokens=4096)
        data = json.loads(raw)

        issues = [ReviewIssue(**i) for i in data.get("issues", [])]
        resp = ReviewResponse(
            issues=issues,
            summary=data.get("summary", ""),
            overall_status=data.get("overall_status", "changes_requested"),
        )

        self.rag.add(
            documents=[
                f"Review verdict: {resp.overall_status}\n"
                f"Issue count: {len(issues)}\n"
                f"Summary: {resp.summary}"
            ],
            metadatas=[{"type": "review", "status": resp.overall_status}],
        )
        return resp
