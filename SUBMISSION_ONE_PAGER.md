# Fashion Garment Classification & Inspiration Web App  
**Submission summary — what we built and how to evaluate it**

---

## 1. Product summary

We delivered a **full-stack web application** that matches the case study intent: designers can **upload** garment inspiration photos, get **AI-assisted structured metadata** plus a **natural-language description**, **search and filter** a visual library using dynamic facets, and **annotate** items over time with tags and notes that remain **searchable** and **visually distinct** from AI-generated fields.

The UI is styled as a **retail-grade, production-style** experience (clear header/footer, collapsible filter panel, product-style cards) while remaining easy to run locally with minimal configuration.

---

## 2. Mapping to the one-pager requirements

| Requirement | What we implemented |
|-------------|---------------------|
| **Upload + AI classification** | `POST /v1/library/upload` stores the image (local disk by default), runs classification through a **pluggable adapter**, persists **description + structured attributes** (garment type, style, material, color palette, pattern, season, occasion, consumer profile, trend notes, location + time context). |
| **Multimodal model** | **Default:** `HeuristicImageClassifier` (fast, offline, uses filename cues—good for demos and CI). **Optional:** `OpenAiVisionClassifier` when `CLASSIFIER_BACKEND=openai` and `OPENAI_API_KEY` is set—**true vision** on image bytes. |
| **Search + filtering** | **GET /v1/library** with full-text-style `q` over descriptions, attributes, designer tags/notes, and trend notes. **Dynamic facets** built from stored data (not hardcoded). Filters include garment dimensions **and** context (continent, country, city, year, month, time season), plus pattern, color palette, trend notes, and garment season where applicable. |
| **Designer annotations** | Tags and notes on upload; **PATCH /v1/library/{id}/annotations** to update later; included in search; UI separates **AI** vs **designer** content. |
| **Persistence** | **SQLAlchemy** with **SQLite** by default; **PostgreSQL** via `DATABASE_URL` for a more production-like deployment. |
| **Testing** | **Unit:** model output parsing. **Integration:** location/time (and related) filter behavior. **E2E (API):** upload → classify → filter → annotate. (`backend/tests/`) |
| **Evaluation** | `eval/labeled_test_set.json` (60 labeled samples) + `eval/run_evaluation.py` reporting per-attribute accuracy; README documents how to run it. |
| **Docs & runbook** | Root `README.md` (setup, architecture, Docker Compose). This submission note for reviewers. |

---

## 3. Technical architecture (high level)

- **Frontend** (`frontend/`): **Next.js 15**, **React 18**, **TypeScript** (strict compiler options). Server-rendered home page; client components for upload, gallery annotations, and collapsible filters. API base URL via `NEXT_PUBLIC_API_BASE_URL`.

- **Backend** (`backend/`): **FastAPI**, **Pydantic v2**, layered design:
  - **Routes** → **services** (library + classification runner) → **repository** (SQL) + **storage** (local/S3).
  - **Classifiers** isolated behind a common interface (heuristic vs OpenAI).
  - **Optional scale paths:** `CLASSIFICATION_EXECUTION` = `sync` (default), `background` (FastAPI tasks), or `arq` + **Redis** worker; **S3** storage backend when configured.

- **Why this shape:** mirrors how a real product would separate **UI**, **API contract**, **domain logic**, **data access**, **object storage**, and **model inference**—so we can swap SQLite→Postgres, local→S3, heuristic→hosted vision, and sync→queued jobs without rewriting the core product flow.

---

## 4. How to run and smoke-test (minimal path)

**No OpenAI, no S3, no Redis required** for a full demo.

1. **Backend:** copy `backend/.env.example` → `backend/.env`; keep `CLASSIFIER_BACKEND=heuristic`, `STORAGE_BACKEND=local`, `CLASSIFICATION_EXECUTION=sync`. From `backend/`: `pip install -e ".[dev,all]"` then `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
2. **Check:** `curl http://127.0.0.1:8000/health` → `{"status":"ok"}`.
3. **Frontend:** `frontend/.env.local` with `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`, then `npm install` && `npm run dev`.
4. **Browser:** open `http://localhost:3000` — upload an image, apply filters, edit annotations.

**Automated:** from `backend/`, run `pytest`.

**Optional:** set `CLASSIFIER_BACKEND=openai` + API key for vision; set `STORAGE_BACKEND=s3` + bucket/credentials for object storage; set `CLASSIFICATION_EXECUTION=arq` + `REDIS_URL` and run the ARQ worker (see `README.md`).

---

## 5. Model evaluation (honest scope)

- **Dataset:** `eval/labeled_test_set.json` contains **60** labeled entries (synthetic filenames + expected attributes) so evaluation is **reproducible without downloading 50–100 external images** into the repo. The script measures **exact-match accuracy** on selected fields (e.g. garment type, style, material, occasion, country).
- **Strengths / limits:** The **heuristic** model is **deterministic and fast** and scores well when filenames encode location/garment hints; it is **not** a pixel-level fashion model. **OpenAI vision** is the path for realistic garment understanding from pixels, at API cost.
- **Improvement with more time:** Curate a **real** 50–100 image set (e.g. licensed fashion photos), human labels, confusion matrices per attribute, fine-tuned or specialized vision model, and calibration for color/pattern attributes.

---

## 6. Trade-offs and assumptions (timeboxed POC)

- **Heuristic default:** prioritizes **working end-to-end** for every reviewer machine without API keys.
- **Facets from completed items only:** pending/failed rows use stub metadata so filters stay meaningful.
- **Repository layout:** application code lives under `backend/app` and `frontend/` rather than a single top-level `/app` folder; behavior and README align with the brief’s intent.
- **Branding:** UI uses **retail-inspired** patterns and disclaimer in the footer; **not** affiliated with Walmart Inc.

---

## 7. Repository map (quick reference)

| Path | Purpose |
|------|---------|
| `frontend/` | Next.js UI, components, strict TS |
| `backend/app/` | FastAPI app, services, classifiers, storage, worker hooks |
| `backend/tests/` | Unit, integration, API E2E |
| `eval/` | Labeled set + `run_evaluation.py` |
| `docker-compose.yml` | Postgres + Redis + API + worker + frontend (optional) |
| `README.md` | Setup, env vars, architecture |
| **This file** | Submission narrative for reviewers |

---

*Prepared for case-study submission — concise overview of scope, architecture, and how to verify behavior locally.*
