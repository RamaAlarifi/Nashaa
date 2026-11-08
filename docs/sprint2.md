# Sprint 2 implementation

Sprint 2 extends the existing FastAPI, SQLAlchemy/PostgreSQL and Next.js application. It covers US09–US16 and FR06–FR09/FR11–FR15. The existing opaque-session authentication, provider interface, typed API client, visual components and role navigation are retained.

## Features

| Story | Implementation |
|---|---|
| US09 | Owner challenge drafts, optional own-idea link, explicit approval before publication, editing and closure |
| US10 | Published challenge discovery with search, industry, location and skill filters |
| US11 | Verified innovator proposals with approach, deliverables, timeline and optional SAR cost |
| US12 | Comparable proposals and one atomic collaborator selection |
| US13 | Verification requests, decision history, administrator review and eligibility updates |
| US14 | Contact preferences, context-specific contact requests, accepted conversations and text messages |
| US15 | Structured project funding and explained investor suggestions |
| US16 | Investment preferences/history, explained ranked registered projects and separately approved assessment access |

Sprint 1 carryover improvements include Save and Assess, stale-assessment feedback, inactive-account login rejection and session recovery after temporary server failures. ORM uniqueness declarations now match the existing Sprint 1 migration instead of proposing equivalent but structurally different indexes.

## Important workflow rules

- Saving a challenge creates a draft. Publishing requires explicit owner approval and valid publication fields. Editing published content returns it to draft for renewed approval. Challenges with submitted proposals cannot be edited; close the challenge and create a revised draft instead. Closed challenges cannot be edited.
- One proposal per innovator per challenge is supported. Selection closes the challenge, marks the selected proposal, marks other proposals not selected, and creates one collaboration. Reselection, proposal withdrawal and collaboration progress are outside this initial implementation.
- Proposal submission, closure and selection lock the same PostgreSQL challenge row. Uniqueness constraints prevent duplicate proposals and conflicting collaborations.
- Verification is platform approval, not government identity verification. Participants provide professional background and an optional reference. Do not upload identity documents. Administrators cannot publicly register themselves or review their own request.
- Messaging requires both accounts to be active and approved. Its context must connect a business owner with an innovator around a published/relevant challenge, or with an investor around a registered idea. Contact requests require recipient acceptance unless the recipient allows open contact. Closed contact blocks messaging.
- Revoked contact permission blocks both message reads and sends. Historical messages remain stored. A newly accepted permission reuses the conversation and replaces its current grant. Closing a challenge does not remove access to its submitted proposal context.
- A private idea is excluded from investor project discovery. Owners may still see investor suggestions for their own private idea, but must choose registered visibility before initiating idea-context contact or sharing an assessment.

## Assessment sharing

Sharing is an explicit grant to a named active investor for one successful assessment version. The owner previews the seven visible assessment sections and approves access. A regenerated result does not replace or extend an earlier grant.

The investor receives the permitted idea summary, approved assessment sections, revision and stale-result information. Raw input snapshots, failed attempts and internal errors are excluded. Existing owner assessment endpoints remain owner-only.

Manual revocation blocks access. Changing an idea to private through either update route revokes all its grants; returning it to registered visibility does not restore those grants. A new owner approval is required. Data already read or copied cannot be recalled. Opportunity and sharing foreign keys prevent silent deletion of their history when deleting an idea.

## Matching

One deterministic service serves owner suggestions and investor project ranking. Industry and stage must match. Available factors use weights of industry 35, stage 25, funding 20, location 10 and history 10. Funding boundaries are inclusive. Optional mismatches score zero; unavailable factors are excluded from the denominator and disclosed. Missing investment history is supported.

Results show the normalised score, available-factor coverage, reasons, mismatches, missing data and history sources. Stable identifiers break equal-score ties. These are transparent prototype rules, not predictions of investment success. Free-text Sprint 1 budgets are retained; validated SAR funding is saved separately.

## Migrations and local demo

Back up the database before upgrading an existing installation. Never remove the PostgreSQL volume to apply a migration.

```powershell
docker compose up -d
docker compose exec backend alembic upgrade head
```

`0003_sprint2` adds eleven opportunity tables and safe user/profile defaults. `0004_contact_context` requires exactly one idea or challenge context for contact requests. Existing users are unverified until reviewed; existing profiles require a contact request by default. New lifecycle strings use explicit checks; existing Sprint 1 enums retain their uppercase database representation and lowercase API values.

Add fictional demonstration data explicitly:

```powershell
docker compose exec backend python -m app.seed.sprint2
```

The command is disabled in production and preserves existing records. It creates fifteen fictional investor preference profiles, ten challenges, example proposals, history with fictional source labels, and approved/pending/rejected verification examples. It uses the existing fictional demo accounts and password documented by the seed module. It does not contact real investors or send external messages.

## Repeatable checks

Run from `backend` with local PostgreSQL available:

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -c pytest-sprint2.ini -p no:cacheprovider
```

Tests live in `backend/quality`. This preserves the user's staged deletion of the earlier `backend/tests` directory. Historical Sprint 1 regressions were retained here with scope-only assertions updated. Tests create uniquely named disposable PostgreSQL databases; they do not recreate the application database. Coverage includes validation, API permissions, visibility, failure recovery, migration preservation, independent-session concurrency and complete journeys. Mock AI is used for repeatability.

Run from `frontend`:

```powershell
npm run check
npm run build
```

The optional browser journey is `frontend/e2e/sprint2.cjs`. It requires Playwright and Chrome, a running local demo stack and the fictional demo administrator. If Playwright is provided outside this repository, set `NASHAA_PLAYWRIGHT_MODULE` to its module directory. Set `NASHAA_E2E_OUTPUT` for the JSON results and screenshots; `NASHAA_E2E_BASE` overrides localhost:3000. The test creates uniquely named fictional accounts and records which remain in the local demo database for inspection. It exercises all four roles, proposal selection, messaging, investor settings, assessment sharing/revocation and a phone viewport. It is not intended for production.

`frontend/e2e/validation.cjs` additionally checks invalid stage feedback, an invalid funding range and the zero-funding boundary. Development Compose enables source polling so changes on Windows bind mounts reach the frontend reliably.

Academic screenshots and Pass/Fail tables should use actual execution evidence. Current execution evidence is maintained separately from this design and implementation explanation.

## Deferred scope

Collaboration progress/completion, customer leads, outreach, ratings, issue reports, general moderation, payments, voice/video, attachments and real-time socket delivery remain outside Sprint 2. Messages use refresh/polling. The current browser journey covers Chrome desktop and a phone-sized viewport; separate Edge, Firefox, screen-reader and workload evaluations are still required before claiming those forms of compatibility.
