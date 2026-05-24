"""
NeuraArchitect — turns a feature spec into a system design.

Pipeline:
  1. Pull related prior designs from RAG (own collection: 'architect').
  2. Ask Groq for a structured JSON design.
  3. Parse into ArchitectResponse, persist this design back into RAG.
"""
import json
import sys
import os
from pathlib import Path

# Allow running as a script or as a module
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from services.shared.llm_client import NeuraLLM
from services.shared.rag import NeuraRAG
from services.shared.schemas import ArchitectRequest, ArchitectResponse


SYSTEM_PROMPT = """You are NeuraArchitect, the system-design agent in Neura-flow AI.

You take a feature spec and produce a complete system design as JSON with this exact shape:
{
  "summary": "<1-2 sentence what we are building>",
  "stack": "<chosen technology stack>",
  "endpoints": [
    {"method":"POST","path":"/x","summary":"...","request_body":{...},"response_body":{...}}
  ],
  "db_schema": [
    {"name":"users","columns":[{"name":"id","type":"int","note":"pk"}, ...]}
  ],
  "rationale": "<why this design — trade-offs, alternatives considered>"
}

Rules:
- Output JSON only, no prose outside JSON.
- Prefer the user's target_stack unless it's clearly wrong for the constraints.
- Keep the design implementable, not academic. Senior-engineer flavor.
- If constraints conflict, surface that in 'rationale' and pick the safer path.
"""


class NeuraArchitect:
    def __init__(self):
        self.llm = NeuraLLM()
        self.rag = NeuraRAG(collection="architect")

    def design(self, req: ArchitectRequest) -> ArchitectResponse:
        context = self.rag.context_block(req.feature_spec, k=3)

        user_prompt = (
            f"{context}\n\n" if context else ""
        ) + (
            f"FEATURE SPEC:\n{req.feature_spec}\n\n"
            f"TARGET STACK: {req.target_stack}\n"
            f"CONSTRAINTS: {json.dumps(req.constraints or {}, indent=2)}\n\n"
            "Return the JSON design now."
        )

        raw = self.llm.json_chat(SYSTEM_PROMPT, user_prompt, max_tokens=4096)
        data = json.loads(raw)
        design = ArchitectResponse(**data)

        # Save this design to RAG so future requests can reference it.
        self.rag.add(
            documents=[
                f"Feature: {req.feature_spec}\nStack: {design.stack}\n"
                f"Summary: {design.summary}\nRationale: {design.rationale}"
            ],
            metadatas=[{"type": "design", "stack": design.stack}],
        )
        return design
