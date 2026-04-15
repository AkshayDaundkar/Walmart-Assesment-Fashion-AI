# Fashion Garment Classification & Inspiration App

Production-oriented full-stack implementation for the case study.

## Stack

- `frontend/` — Next.js 15 + React 18 + TypeScript (strict mode).
- `backend/` — FastAPI + Pydantic v2 + SQLAlchemy (SQLite or PostgreSQL).
- `eval/` — evaluation script and labeled test set (60 samples).
- `backend/tests/` — unit, integration, and API-level end-to-end tests.

## Core Features

- Upload image + classify via a pluggable multimodal adapter (heuristic or OpenAI vision).
- Object storage abstraction: **local disk** or **S3-compatible** backends.
- **Async classification**: `sync` (default), `background` (FastAPI `BackgroundTasks`), or `arq` + Redis worker.
- Persistent library with classification status: `pending` | `completed` | `failed`.
- `GET /v1/library/{item_id}` for polling after async uploads.
- Dynamic facets from completed items only; search across AI text + designer annotations.
- Designer annotations: `PATCH /v1/library/{item_id}/annotations`.
- Request observability: `X-Request-ID` on responses; structured logging hook via `LOG_LEVEL`.

## Architecture (backend)

| Layer | Role |
|--------|------|
| `app/api/` | HTTP routes, validation |
| `app/services/classifiers/` | `HeuristicImageClassifier`, `OpenAiVisionClassifier` |
| `app/services/classification_runner.py` | Retry-safe classify → persist |
| `app/repositories/` | SQLAlchemy-backed `LibraryRepository` |
| `app/db/` | Engine factory + schema/migrations |
| `app/storage/` | `LocalObjectStorage`, `S3ObjectStorage` |
| `app/worker_tasks.py` | ARQ job: load bytes from storage → classify |

## Configuration

See `backend/.env.example`. Important variables:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | e.g. `postgresql+psycopg://user:pass@host:5432/db` (omit for SQLite + `DATABASE_PATH`) |
| `STORAGE_BACKEND` | `local` or `s3` |
| `CLASSIFIER_BACKEND` | `heuristic` or `openai` |
| `OPENAI_API_KEY` | Required when `CLASSIFIER_BACKEND=openai` |
| `CLASSIFICATION_EXECUTION` | `sync`, `background`, or `arq` |
| `REDIS_URL` | Required when `CLASSIFICATION_EXECUTION=arq` |
| `PUBLIC_ASSETS_BASE_URL` | Base URL for generated image links (e.g. API or CDN) |

## Local run

Run the API and UI on your machine only (`127.0.0.1` / `localhost`); no cloud deploy is required for the case study.

### 1. Environment files

**Backend** — copy and edit (paths assume you start the API from the `backend/` directory):

```bash
cp backend/.env.example backend/.env
```

Minimum to work locally: leave SQLite defaults, set `CORS_ORIGINS` to include `http://localhost:3000`, and use `DATABASE_PATH=data/library.db` + `STORAGE_ROOT=data` if you run uvicorn from `backend/` (creates `backend/data/` for the DB and uploads).

**Frontend**:

```bash
cp frontend/.env.example frontend/.env.local
# Ensure NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 2. Start API first, then UI

**Terminal A — API**

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,all]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Smoke test:

```bash
curl -s http://127.0.0.1:8000/health
# expect: {"status":"ok"}
```

**Terminal B — UI**

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**. If the grid is empty and the API is down, you’ll see the empty state hint.

### 3. Automated tests (API)

```bash
cd backend
source .venv/bin/activate
pytest
```

### Docker Compose (Postgres + Redis + ARQ worker)

```bash
docker compose up --build
```

Stack: Postgres, Redis, API (`CLASSIFICATION_EXECUTION=arq`), **worker** (`arq app.worker_settings.WorkerSettings`), frontend. Shared volume `/data` for local uploads inside containers.

## API

- `GET /health`
- `GET /v1/library` — search + filters
- `GET /v1/library/{item_id}` — single item (polling)
- `POST /v1/library/upload` — multipart upload
- `PATCH /v1/library/{item_id}/annotations`

## Tests

```bash
cd backend
pytest
```

- Parser unit test: `tests/test_model_output_parser.py`
- Filter integration: `tests/test_library_filters.py`
- E2E upload → classify → filter → annotate: `tests/test_api_e2e.py`

## Evaluation

```bash
PYTHONPATH=backend python3 eval/run_evaluation.py
```

Uses `CLASSIFIER_BACKEND` from the environment (defaults to heuristic for reproducible offline metrics).

## Further hardening (optional)

- Alembic migrations for Postgres versioning.
- OIDC auth, RBAC, audit trail.
- Playwright E2E against running stack.
- Dead-letter queue and metrics (Prometheus/OpenTelemetry) on worker and API.
# Walmart-Assesment-Fashion-AI
