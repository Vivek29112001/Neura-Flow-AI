"""
NeuraFrontend — turns an ArchitectResponse into Next.js / React code.

Generates:
- App Router pages for each major resource
- A typed API client matching the design's endpoints
- Tailwind-styled components (forms, lists, detail views)
- package.json, tsconfig, tailwind config

Maintains its own Chroma collection ('frontend') so generated code stays
consistent with prior UI conventions across runs.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from services.shared.llm_client import NeuraLLM
from services.shared.rag import NeuraRAG
from services.shared.schemas import (
    FrontendRequest,
    FrontendResponse,
    GeneratedFile,
)


SYSTEM_PROMPT = """You are NeuraFrontend, the frontend-codegen agent in Neura-flow AI.

You receive a system design and produce a complete Next.js + Tailwind app as JSON:
{
  "files": [
    {"path":"app/page.tsx","content":"<full file>","language":"tsx"},
    {"path":"lib/api.ts","content":"<typed api client>","language":"ts"},
    {"path":"package.json","content":"{...}","language":"json"},
    ...
  ],
  "install_commands": ["npm install"],
  "notes": "<brief notes for human reviewer>"
}

Rules:
- Output valid JSON only.
- Next.js 14 App Router + TypeScript + Tailwind by default.
- One page per major resource in db_schema (list + detail + create form).
- Generate a typed API client in `lib/api.ts` that matches the design's endpoints exactly.
- Use Server Components where reasonable; Client Components only when needed (forms, interactivity).
- No external UI libs unless absolutely necessary. Tailwind utility classes only.
- Include `package.json` with correct deps and `tailwind.config.ts`.
- All files must be complete and runnable — no TODOs or `...` stubs.
"""


class NeuraFrontend:
    def __init__(self):
        self.llm = NeuraLLM()
        self.rag = NeuraRAG(collection="frontend")

    def generate(self, req: FrontendRequest) -> FrontendResponse:
        design_json = req.design.model_dump_json(indent=2)
        context = self.rag.context_block(req.design.summary, k=3)

        user_prompt = (
            (f"{context}\n\n" if context else "")
            + f"DESIGN:\n{design_json}\n\n"
            + f"FRAMEWORK: {req.framework}\n"
            + f"API BASE URL: {req.api_base_url}\n\n"
            + "Return the JSON of files now."
        )
        raw = self.llm.json_chat(SYSTEM_PROMPT, user_prompt, max_tokens=8192)
        data = json.loads(raw)

        files = [GeneratedFile(**f) for f in data.get("files", [])]
        resp = FrontendResponse(
            files=files,
            install_commands=data.get("install_commands", ["npm install"]),
            notes=data.get("notes"),
        )

        self.rag.add(
            documents=[
                f"Frontend for: {req.design.summary}\n"
                f"Framework: {req.framework}\n"
                f"Files: {[f.path for f in files]}\n"
                f"Notes: {resp.notes or ''}"
            ],
            metadatas=[{"type": "frontend_gen", "framework": req.framework or ""}],
        )
        return resp
