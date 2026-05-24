"""
NeuraBackend — turns an ArchitectResponse into runnable backend code.

The agent asks Groq to emit a strict JSON list of files, then re-hydrates
them as GeneratedFile objects. RAG collection ('backend') accumulates
patterns from past generations so the agent stays consistent with prior
code conventions.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from services.shared.llm_client import NeuraLLM
from services.shared.rag import NeuraRAG
from services.shared.schemas import (
    BackendRequest,
    BackendResponse,
    GeneratedFile,
    ArchitectResponse,
)


SYSTEM_PROMPT = """You are NeuraBackend, the backend-codegen agent in Neura-flow AI.

You receive a system design and produce production-quality backend code as JSON:
{
  "files": [
    {"path":"app/main.py","content":"<full file contents>","language":"python"},
    ...
  ],
  "install_commands": ["pip install fastapi uvicorn sqlalchemy ..."],
  "notes": "<brief notes for the human reviewer>"
}

Rules:
- Output valid JSON only.
- Generate FastAPI + SQLAlchemy by default (unless the design specifies otherwise).
- Every endpoint in the design must have a real handler — no `pass` placeholders.
- Include Pydantic request/response models, DB models, and a startup that creates tables.
- File contents must be complete and runnable — no '...' or 'TODO' fillers.
- Use type hints everywhere. Senior-engineer code, not tutorial code.
"""


class NeuraBackend:
    def __init__(self):
        self.llm = NeuraLLM()
        self.rag = NeuraRAG(collection="backend")

    def generate(self, req: BackendRequest) -> BackendResponse:
        design_json = req.design.model_dump_json(indent=2)
        context = self.rag.context_block(req.design.summary, k=3)

        user_prompt = (
            (f"{context}\n\n" if context else "")
            + f"DESIGN:\n{design_json}\n\n"
            + "Return the JSON of files now."
        )
        raw = self.llm.json_chat(SYSTEM_PROMPT, user_prompt, max_tokens=8192)
        data = json.loads(raw)

        files = [GeneratedFile(**f) for f in data.get("files", [])]
        resp = BackendResponse(
            files=files,
            install_commands=data.get("install_commands", []),
            notes=data.get("notes"),
        )

        # Store a summary of this generation so future runs can retrieve patterns
        self.rag.add(
            documents=[
                f"Backend for: {req.design.summary}\n"
                f"Files: {[f.path for f in files]}\n"
                f"Notes: {resp.notes or ''}"
            ],
            metadatas=[{"type": "backend_gen", "file_count": len(files)}],
        )
        return resp
