# Nashaa - From Idea to Opportunity

The delivered application contains Sprint 1 (US01-US08): accounts, password recovery, profiles, role dashboards, business ideas, AI assessments, and idea visibility.

## What you can do

Business owners can create, save, view and edit ideas, choose private or registered-user summary visibility, and generate or regenerate assessments. Each assessment records its input and idea revision, and includes market considerations, customers, competitors, indicative costs, next steps, assumptions and sources when available. Failed regeneration preserves the last successful assessment.

Innovators and investors maintain their role-specific profiles and account dashboards. Administrators have an account dashboard and profile; operator-provisioned accounts cannot be created through public registration. Roles and ownership are checked by the API. Registered users can view an idea's shared summary by its workspace link; private details and assessments remain owner-only.

## Run locally with Docker

Requirements: Docker Engine/Desktop and Docker Compose v2.

```powershell
Copy-Item .env.example .env
# For a local fictional demo only, set EXPOSE_RESET_TOKENS=true in .env.
docker compose up -d --build --wait
docker compose exec backend python -m app.seed.seed
```

Open http://localhost:3000. API documentation: http://localhost:8000/api/docs. Health: http://localhost:8000/health. The six application tables are created by Alembic at backend startup. PostgreSQL uses persistent storage. Development ports bind only to localhost.

Seeding is optional, disabled by default, and refused in production. It adds 16 fictional accounts and 12 fictional ideas without duplicating them on subsequent runs. Demo password: `Password123!`. Example accounts: `owner1@nashaa.sa`, `innov1@nashaa.sa`, `invest1@nashaa.sa`, `admin@nashaa.sa`. Never load these accounts into a real deployment.

```powershell
docker compose build
docker compose up -d --wait
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f database
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
docker compose exec backend pytest -p no:cacheprovider
docker compose exec frontend npm run check
docker compose stop
docker compose down
```

`down` retains PostgreSQL storage. Do not use `down -v` on a database you need to keep. Docker logs rotate at 10 MB with three retained files per service. Health probes verify PostgreSQL, API database connectivity, and frontend HTTP availability.

## Password recovery

Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM`, optional `SMTP_USERNAME` / `SMTP_PASSWORD`, and `RESET_URL`. SMTP uses STARTTLS. Production requires HTTPS frontend/reset URLs and SMTP configuration. Reset secrets are hashed, expire, are single-use, and revoke existing sessions and other reset links when consumed. Email links carry tokens in the URL fragment to avoid access-log exposure.

For a local demo without email, explicitly set `EXPOSE_RESET_TOKENS=true`; a reset link appears on the recovery screen. Leave this false on any shared environment. It is forbidden in production. No real email provider credentials are included.

## AI provider

`AI_PROVIDER=mock` runs offline with clearly labeled fictional assessments. For live AI set `AI_PROVIDER=gemini`, `GEMINI_API_KEY`, and `GEMINI_MODEL` to an available model in your Google account. Consult the [official model list](https://ai.google.dev/gemini-api/docs/models) and [retirement schedule](https://ai.google.dev/gemini-api/docs/deprecations). No retired model is hard-coded as a default.

Keys stay in the backend. Live generation sends the submitted idea to the selected provider. Sources are reported only when available; general-knowledge output is identified as such. Costs are estimates and assumptions require validation. A provider failure never replaces a valid saved result.

## Production configuration

Create a separate protected environment file with a strong, URL-safe PostgreSQL password, SMTP settings, HTTPS `FRONTEND_ORIGIN` and `RESET_URL`, and the chosen AI settings. Set `APP_ENV_FILE` to that file's path. For example:

```powershell
$env:APP_ENV_FILE = '.env.production'
docker compose --env-file .env.production -p nashaa-production -f docker-compose.production.yml up -d --build --wait
```

Development and production use different Compose project names and independent volumes. Production has no source mounts or reload process, runs app containers as non-root, forces demo seeding/token exposure off, and does not publish PostgreSQL or FastAPI ports. Next.js proxies `/api` to the backend service. Put an HTTPS reverse proxy in front of localhost:3000 and apply deployment-level request limits. TLS termination and real SMTP/AI accounts belong to the deployment environment.

Provision a real administrator from the trusted operator terminal:

```powershell
docker compose -p nashaa-production -f docker-compose.production.yml exec backend python -m app.create_admin
```

Passwords are entered through a hidden prompt. `.env` files and backups are ignored by Git and excluded from image build contexts. Never copy production secrets into frontend variables.

## Backup and restore

Back up before upgrading an existing database. On Windows, use the binary-safe helper:

```powershell
./scripts/backup-db.ps1
# Production: ./scripts/backup-db.ps1 -ComposeFile docker-compose.production.yml -Project nashaa-production
```

Store another encrypted copy outside the Docker host. To verify a backup, restore into a NEW database, keeping the source intact (substitute your backup path and database user):

```powershell
docker compose cp .backups/nashaa-TIMESTAMP.dump database:/tmp/restore.dump
docker compose exec database createdb -U nashaa nashaa_restore
docker compose exec database pg_restore --exit-on-error -U nashaa -d nashaa_restore /tmp/restore.dump
docker compose exec database psql -U nashaa -d nashaa_restore -c "SELECT count(*) FROM users"
```

Then start a separately configured backend against the restored database, run migrations, and verify accounts/ideas/assessments before switching service configuration. A schema downgrade does not recover removed column values; use the pre-upgrade archive for full recovery. Avoid binary shell redirection in Windows PowerShell; use container files and `docker compose cp`.

Existing databases at `0001_initial` upgrade forward to `0002_sprint1_only`. Historical migration semantics are retained with frozen enums. Do not blindly `stamp head` on an unversioned database: back it up, compare its schema with `0001_initial`, and adopt that revision only after confirming equivalence.

## Development and validation

Source: `frontend/` (Next.js/TypeScript), `backend/` (FastAPI/SQLAlchemy/PostgreSQL). Tests use a separate disposable `nashaa_test` database, built with the real migrations. Never point the test suite at a production database server.

```powershell
cd frontend
npm ci
npm run check
npm run build
```

The approved palette, Poppins typography, original bilingual outlined logos, tagline, icon and favicon are retained. Shared components implement focus states, labeled controls, responsive layout and reduced-motion support. See `docs/interface-guide.md`, `docs/erd.md`, and `docs/sprint1.md`. `Nashaa_Guide.md` remains the unchanged full project reference.
