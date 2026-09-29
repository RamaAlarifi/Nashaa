# Sprint 1 scope inventory

Inspection date: 27 September 2026. This is an engineering change record; the client-facing README describes the delivered application only. The full project guide was read as reference and was not edited.

## Before changes

The checkout already implemented US01-US08 rather than a complete marketplace. Baseline testing passed 57 tests. Six application tables and Alembic revision `0001_initial` were present in the used local database. Foreign keys: profiles/sessions/password_resets/business_ideas to users; assessments to business_ideas. No tables depended on either removed column.

Working baseline: account creation/access, sessions and logout, reset-token lifecycle, own-profile edits, owner dashboard, idea CRUD/revisions, owner-only assessment history, private/registered visibility enforcement. Gaps: no production reset email transport; no role-specific profile inputs; permitted shared summaries displayed as errors; public admin registration accepted by the API; provider-construction errors escaped failure persistence; empty AI sections could pass validation; Docker test command lacked tests; production proxy used a build-time default host; original branding assets were not wired in.

## Later-sprint inventory

No exclusive feature pages, routers, services, feature tables, or seed datasets existed for challenges, proposals, messaging, collaboration, investor matching, customer leads, outreach, ratings, reports or moderation.

The actual remnants were:

| Location | Removed content |
| --- | --- |
| `backend/app/routers/dashboard.py` | Future challenges/proposals/ranked-project messages and administrator moderation actions |
| `frontend/app/dashboard/page.tsx` | Future-release cards and administrator placeholders |
| `backend/app/models/user.py`, `schemas/user.py`, `models/enums.py` | Verification status field and live enum |
| `backend/app/models/profile.py`, `schemas/profile.py`, `models/enums.py` | Messaging/contact-request preference field and live enum |
| `frontend/app/profile/page.tsx`, `frontend/lib/types.ts` | Contact preference form and obsolete type fields |
| `backend/app/seed/seed.py`, `services/auth.py` | Contact-preference seed/default values |
| `backend/tests/test_dashboard.py` | Assertions requiring future moderation actions |
| `README.md`, `docs/erd.md`, `docs/sprint1.md` | Future-feature descriptions and obsolete schema claims |
| Live database | `users.verification_status`, `profiles.contact_preference` |

## Shared code retained

All six application tables, all Sprint 1 routers/services/models, all four roles, account status checks, profile visibility, role-specific JSON, assessment input/history/status, and unranked visibility summaries remain. The idea's `current_challenges` field is planning context required by Sprint 1, not the challenge marketplace. Shared cards, forms, input controls, states, layout, navigation, branding tokens and responsive CSS remain.

## Safe removal sequence followed

1. Inspect source, migration and Docker configuration, live tables and foreign keys, and screen code; attempt connected browser inspection.
2. Report findings before editing; archive source/config and PostgreSQL.
3. Restore the dump to a separate database and check counts.
4. Remove UI/API/model remnants and replace placeholders with functional role account workspaces.
5. Freeze original migration enums without altering its DDL semantics; add `0002_sprint1_only` for the used database.
6. Upgrade the restored copy and verify all account/idea/assessment counts.
7. Fix Sprint 1 gaps, seed idempotency, Docker startup, tests and documentation.
8. Build isolated development/production stacks, run acceptance checks, then upgrade the original local stack while retaining its named volume.

No whole source file was exclusively a later-sprint feature; removal happened within shared files. Historical migration declarations remain solely so an existing database can be upgraded and restored safely.
