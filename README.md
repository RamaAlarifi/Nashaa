# Nashaa — AI Platform for Saudi SMEs

Nashaa helps Saudi entrepreneurs and small-business owners move from a business
idea to practical action. This repository contains the **Sprint 1** working
version covering user stories US01–US08.

> All demonstration data is fictional. Do not use real personal data in demos.

## Stack

- **Web interface:** Next.js (App Router, TypeScript, Tailwind CSS)
- **Server:** Python + FastAPI
- **Database:** PostgreSQL
- **AI:** an external LLM behind a single swappable server component
  (Google Gemini configured, with a mock provider for offline dev/tests)
- **Source control:** Git

## Project layout

```
Nashaa/
├── backend/        FastAPI app (Python)
│   ├── app/
│   │   ├── models/         SQLAlchemy models
│   │   ├── schemas/        Pydantic API contracts
│   │   ├── routers/        API endpoints
│   │   ├── services/       business logic
│   │   ├── ai/             swappable AI provider (gemini / mock)
│   │   ├── core/           security & auth dependencies
│   │   ├── seed/           fictional demo data
│   │   └── main.py         app entrypoint
│   └── tests/      pytest suite (US01–US08)
├── frontend/       Next.js app
│   ├── app/        screens (login, dashboard, ideas, assessment, …)
│   ├── components/ shared UI
│   └── lib/        API client, auth context, types
├── docker-compose.yml   local PostgreSQL
└── Nashaa_Guide.md       full project guide
```

## Quick start (development)

### Prerequisites

- Node 22+, npm 10+
- Python 3.10+
- Docker (for PostgreSQL)

### 1. Start PostgreSQL

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

# Copy the example env and edit secrets if needed (the mock AI provider works
# with no API key).
copy .env.example .env            # Windows  (cp on macOS/Linux)

# Create tables and load fictional demo data.
python -m app.seed.seed

# Run the API server (http://127.0.0.1:8000, docs at /api/docs).
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev          # http://127.0.0.1:3000
```

The Next.js dev server proxies `/api/*` to the FastAPI backend
(see `frontend/next.config.js`), so no CORS setup is needed in development.

### Run the tests

```bash
cd backend
.venv\Scripts\python.exe -m pytest
```

## Demo accounts

All accounts use the password: **`Password123!`**

| Email | Role | Notes |
|---|---|---|
| `owner1@nashaa.sa` | Business owner | owns GreenBox (has a successful assessment) |
| `owner2@nashaa.sa` | Business owner | owns QuickRoute (failed assessment) |
| `owner3@nashaa.sa` | Business owner | owns CareLine (in-progress assessment) |
| `innov1@nashaa.sa` | Innovator | basic dashboard (Sprint 2 features pending) |
| `invest1@nashaa.sa` | Investor | basic dashboard (Sprint 2 features pending) |
| `admin@nashaa.sa` | Administrator | admin entry points (Sprint 2/3 pending) |

## Using the real Gemini AI

The backend ships with a **mock** AI provider that returns a clearly-labeled,
valid assessment, so you can run everything without an API key. To use Google
Gemini:

1. Edit `backend/.env`:
   ```
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_key_here
   ```
2. Restart the backend.

The provider lives behind a single component (`backend/app/ai/`), so it can be
swapped without touching the rest of the app (project rule, section 9).

## Sprint 1 scope (US01–US08)

- US01 Create & access an account (register / login / logout / session)
- US02 Recover account access (single-use, time-limited password reset)
- US03 Maintain a profile (role cannot be changed here)
- US04 Role-based dashboard (business owner / innovator / investor / admin)
- US05 Submit & manage a business idea (revision tracking)
- US06 Receive an AI business assessment
- US07 Refine an assessment (previous result preserved on failure; no duplicate
  concurrent requests)
- US08 Control idea visibility (private / registered), enforced by the server

See `docs/sprint1.md` for the full Sprint 1 record (tests, deliverables, status).
