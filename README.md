# Nashaa — From Idea to Opportunity

Nashaa is a web app where a business owner can save their idea, ask the AI to
assess it, and share a short summary. Innovators and investors get their own
dashboards and profiles, and an admin can manage accounts.

This is our **Sprint 1** build (user stories US01–US08): sign up, login,
password recovery, profiles, role dashboards, business ideas, AI assessments,
and idea visibility.

---

## What you need

- **Git** — to download the code
- **Docker Desktop** (with Docker Compose v2) — the easy way to run everything

That's it for the easy path. Docker starts the database, the backend (FastAPI),
and the frontend (Next.js) for you.

---

## Step 1 — Get the code

```powershell
git clone https://github.com/RamaAlarifi/Nashaa.git
cd Nashaa
```

If the repo is private you'll be asked for a username and a **Personal Access
Token** (not your password). Make one at
https://github.com/settings/tokens/new with the **`repo`** scope.

---

## Step 2 — Make your `.env` file

The app reads settings from a file called `.env`. We give you a ready-made
example, just copy it:

```powershell
Copy-Item .env.example .env
```

The defaults in `.env.example` work out of the box for a local demo:

- `AI_PROVIDER=mock` → the AI returns clearly-labeled **fake** assessments, so
  you don't need an API key.
- Database password and secret key are filled with demo values.

> Don't commit `.env`. It's already in `.gitignore`.

### (Optional) Use real Gemini AI

If you want real AI answers instead of the fake ones, edit `.env`:

```
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Get a key from https://aistudio.google.com/app/apikey. Pick a current model
name from the Gemini docs.

### (Optional) Password recovery without email

By default, password reset needs an SMTP email server. For a local demo
without email, set this in `.env`:

```
EXPOSE_RESET_TOKENS=true
```

Then a reset link appears right on the "Forgot password" screen. Leave it
`false` on any shared machine — never use it in production.

---

## Step 3 — Run it (Docker, the easy way)

```powershell
docker compose up -d --build --wait
```

The first run takes a few minutes (it downloads and builds images). When it
finishes:

- **Frontend (the website):** http://localhost:3000
- **API docs (Swagger):** http://localhost:8000/api/docs
- **Health check:** http://localhost:8000/health

The database tables are created automatically by Alembic when the backend
starts. PostgreSQL data is saved in a Docker volume, so it stays after restart.

---

## Step 4 — (Optional) Load demo data

Want some fake accounts and ideas to look at? Run this once:

```powershell
docker compose exec backend python -m app.seed.seed
```

It adds 16 fake accounts and 12 fake ideas. Running it again won't duplicate
them. **Demo password for all of them:** `Password123!`

| Role          | Login email        |
| ------------- | ------------------ |
| Business owner | `owner1@nashaa.sa`  |
| Innovator    | `innov1@nashaa.sa`  |
| Investor     | `invest1@nashaa.sa` |
| Admin        | `admin@nashaa.sa`   |

> These are fictional. Never load them into a real deployment.

---

## Useful commands

```powershell
# See live logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f database

# Stop the app (keeps your data)
docker compose stop

# Start again
docker compose up -d --wait

# Stop and remove containers (data still saved in the volume)
docker compose down

# Delete everything including the database data — careful!
docker compose down -v
```

---

## Running without Docker (manual)

If you can't use Docker, you can run the three parts yourself. You'll need
**Python 3.11+**, **Node.js 18+**, and a **PostgreSQL** server running.

### A) Database

Create a database (e.g. `nashaa`) and a user with a password you know.

### B) Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
```

Copy `backend/.env.example` to `backend/.env` and edit it:

- `DATABASE_URL` → point to your local PostgreSQL (use `localhost` as host,
  not `database`).
- Set `SECRET_KEY` to any long random string.
- Keep `AI_PROVIDER=mock` for a quick start.

Then run the migrations and start the API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs will be at http://localhost:8000/api/docs.

### C) Frontend

Open a **new** terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000.

---

## How the code is organized

```
Nashaa/
├─ backend/      FastAPI + SQLAlchemy + PostgreSQL  (Python)
│  ├─ app/        source code
│  ├─ migrations/ Alembic database migrations
│  └─ tests/      pytest tests
├─ frontend/     Next.js + TypeScript + Tailwind
│  ├─ app/        pages
│  ├─ components/ reusable UI
│  └─ lib/        API client, auth, types
├─ docs/         design notes, ERD, sprint docs
├─ scripts/      backup + smoke-test helpers
├─ docker-compose.yml          local dev stack
└─ docker-compose.production.yml  production stack (no source mounts)
```

---

## Running the tests

With Docker:

```powershell
docker compose exec backend pytest -p no:cacheprovider
docker compose exec frontend npm run check
```

Tests use a separate `nashaa_test` database, so they won't touch your demo data.
Never point the test suite at a real/production database.

---

## Troubleshooting

- **Port already in use?** Something else is using 3000, 5432, or 8000. Stop it,
  or change the port in `.env` (`FRONTEND_PORT`, `DATABASE_PORT`, `BACKEND_PORT`).
- **`docker compose` not found?** Install Docker Desktop and make sure
  "Use Compose v2" is on.
- **First `up` is slow?** That's normal — it's building images. Later runs are
  fast.
- **Frontend shows API errors?** Check the backend is healthy:
  http://localhost:8000/health, and look at `docker compose logs backend`.
- **Reset link not showing?** You forgot to set `EXPOSE_RESET_TOKENS=true` in
  `.env`, then run `docker compose up -d --wait` again.

---

## Notes for production

This README is for running the project on your own PC. For a real deployment,
use `docker-compose.production.yml`, put it behind HTTPS, set a strong
PostgreSQL password, real SMTP, and a real `SECRET_KEY`. See `Nashaa_Guide.md`
for the full reference.
