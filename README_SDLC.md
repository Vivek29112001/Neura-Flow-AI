# Neura-flow AI — Phase 2: SDLC Agent Stack

This is the **build layer** of Neura-flow. Phase 1 (`app/`) handles daily intel.
Phase 2 (`services/` + `orchestrator/`) handles the full software development
lifecycle: design → backend code → tests.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              NeuraBuild Orchestrator (LangGraph)                 │
│              POST /build  →  port 8000                           │
└───┬──────────┬──────────┬──────────┬──────────┬──────────────────┘
    ▼          ▼          ▼          ▼          ▼
 ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐ ┌────────┐
 │Arch- │ │Back- │ │ Test │ │ Frontend │ │ Review │
 │itect │ │ end  │ │      │ │          │ │        │
 │ 8001 │ │ 8002 │ │ 8003 │ │   8004   │ │  8005  │
 └───┬──┘ └───┬──┘ └───┬──┘ └─────┬────┘ └────┬───┘
     └────────┴────────┴──────────┴───────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Chroma (RAG)  │
                  │ per-agent     │
                  │ collections   │
                  └───────────────┘
```

Each agent is an independent FastAPI service with its own Chroma collection
(`architect`, `backend`, `test`, `frontend`, `review`). Agents use **RAG**,
not fine-tuning — data updates frequently and we don't want stale weights.

The LangGraph state machine in `orchestrator/graph.py` drives the flow.
Frontend and backend run in **parallel**; review fans in at the end:

```
                ┌─→ frontend ───────────────────────────────┐
START → architect                                           ├→ review → END
                └─→ backend ──→ test_gen ──→ test_run ──────┘
                       │
                       └── (run_tests=false) ────────────────↑
```

Review returns `overall_status`: `approved`, `changes_requested`, or `blocked`.
That's your 20% human gate — if `blocked`, you read the issues and decide.

## Stack

- **LLM:** Groq (Llama 3.3 70B by default — override via `NEURA_LLM_MODEL`)
- **Orchestration:** LangGraph
- **Vector DB:** Chroma (embedded, persisted to disk)
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (local, free)
- **Transport:** FastAPI + httpx between services

## Quick start

```bash
# 1. Set your Groq key
cp .env.example .env  # or edit existing .env
echo "GROQ_API_KEY=your-key-here" >> .env

# 2. Bring up the stack
docker compose up --build

# 3. Trigger a build
curl -X POST http://localhost:8000/build \
  -H "Content-Type: application/json" \
  -d '{
    "feature_spec": "A todo API with users, tasks, and due dates. JWT auth.",
    "target_stack": "FastAPI + SQLAlchemy + Postgres",
    "run_tests": true
  }'
```

Response contains the design, generated backend files, generated test files,
and (if `run_tests=true`) the pytest pass/fail counts.

## Local dev without Docker

```bash
pip install -r services/shared/requirements.txt
pip install -r orchestrator/requirements.txt

# Each in its own terminal:
uvicorn services.neura_architect.main:app --port 8001
uvicorn services.neura_backend.main:app   --port 8002
uvicorn services.neura_test.main:app      --port 8003
uvicorn services.neura_frontend.main:app  --port 8004
uvicorn services.neura_review.main:app    --port 8005
uvicorn orchestrator.main:app             --port 8000
```

## Relationship to Phase 1

Phase 1 (`app/`, `orchestrator.py`) is **untouched**. It continues to run the
daily intel agents (NeuraNews, NeuraJobs, NeuraLearn, NeuraCode, NeuraWatch,
NeuraForge) on its own scheduler. Phase 2 is reached by HTTP, not by import.

## Agents built so far

| Agent | Port | Role |
|---|---|---|
| NeuraArchitect | 8001 | Feature spec → system design (stack, endpoints, db_schema) |
| NeuraBackend   | 8002 | Design → FastAPI + SQLAlchemy code |
| NeuraTest      | 8003 | Backend code → pytest tests + actually runs them |
| NeuraFrontend  | 8004 | Design → Next.js 14 + Tailwind app |
| NeuraReview    | 8005 | Final quality gate, returns issues + overall_status |

## Next agents to add (roster)

- **NeuraUX** — wireframes + component hierarchy (feeds NeuraFrontend)
- **NeuraDB** — migrations, indexes, query plans
- **NeuraDevOps** — Dockerfile, GitHub Actions, Terraform, deploy
- **NeuraMonitor** — Sentry/Grafana/alerting setup
- **NeuraDocs** — README, OpenAPI export, runbooks, ADRs

Each follows the same template: `services/<name>/` with `agent.py`,
`main.py`, `Dockerfile`. Add a node to `orchestrator/graph.py` and an edge.
