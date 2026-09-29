# Sprint 1 delivery record

Date: 27 September 2026. Scope: US01-US08 only. Original local app: http://localhost:3000.

## Delivered behavior

- Registration/login/logout and hashed server sessions; public admin registration rejected, operator CLI provisioning retained.
- Single-use, expiring password recovery with SMTP STARTTLS transport; explicit local-demo links; existing sessions and other reset requests revoked on reset.
- Role-specific editable profiles and basic dashboards for all four roles, with working profile actions.
- Business owners create, save, reopen and edit ideas; all assessment inputs including the title advance the revision when changed.
- All seven assessment sections; malformed/empty content rejected; exceptions including provider setup failure preserve the last successful result.
- PostgreSQL locking prevents simultaneous assessment generation; real concurrent connections are tested.
- Private ideas remain owner-only. Registered viewers see only the permitted summary, with no access to editing or assessments.
- Original bilingual logo artwork, official icon/favicon, Poppins, palette and tagline replace prior logo placeholders.

## Database and recoverability

Source/config archive: `.backups/sprint1-before-20260927/source-config.tar.gz`.
Original PostgreSQL dump: `.backups/sprint1-before-20260927/database.dump`.
The archive includes the pre-existing uncommitted work and local configuration; keep it private.

The dump was restored into `nashaa_restore_sprint1`, then migrated successfully. The original local database was upgraded only after that check. Both retained 17 accounts, 13 business ideas and 6 assessment attempts. The final schema has exactly the six Sprint 1 application tables plus Alembic bookkeeping.

`0002_sprint1_only` removes two unused columns, and fixes uppercase enum server defaults. The first migration's DDL semantics remain unchanged; its enum imports now point to frozen historical definitions. Downgrade can recreate column structure; full pre-change values require restoration from the backup.

## Validation results

- Baseline suite: 57 passed.
- Expanded migrated-PostgreSQL suite: 78 passed, including concurrent assessment requests with separate connections. One dependency deprecation warning from Starlette/AnyIO; no failures.
- Final production backend image: all 78 tests passed. Test setup forces mock AI and disables external email delivery, regardless of deployment environment variables.
- Strict TypeScript check: passed on host and inside Docker.
- Next.js production build: passed, with only Sprint 1 routes in the build manifest.
- Development images built from scratch; fresh isolated PostgreSQL volume migrated and all three services became healthy.
- Production images built and started with an independent database volume; all three services healthy. Backend/database have no published production ports.
- HTTP acceptance checks passed through both frontend proxies: pages and official assets, registration, profiles, dashboards, idea creation/editing, assessment/regeneration, private/shared visibility, cross-owner restrictions, logout, and 404s for excluded routes. Local-demo password recovery and session revocation passed.
- Fictional seed rerun: 16 users and 12 ideas remained unchanged; the second run created zero ideas.
- Restored-backup migration and original-volume upgrade preserved record counts.
- Documented PowerShell binary-safe backup helper ran successfully.
- Clean frontend dependency installation after the PostCSS patch: zero npm advisories reported.
- `Nashaa_Guide.md` SHA-256 remains `4678D6B7347E4A983D44E61E0E32AD73B125207C5E2DCEFBD106423D3C1F52FA`.

## Remaining validation limits

The browser tools reported no available browser, including the in-app browser. Screen source, compiled routes and HTTP responses were checked, but visual mobile/desktop and keyboard/screen-reader acceptance could not be performed in this session.

Real SMTP delivery and paid Gemini requests were not exercised. SMTP behavior is covered with a mocked transport and AI success/failure/malformed/delayed paths use deterministic providers. Configure real credentials/model access and verify those integrations before client deployment. The production startup check used mock AI and non-delivering SMTP settings. HTTPS termination and deployment request limits require the hosting environment described in README.

The full guide contains all three sprints by design; it is unchanged. The application and client-facing README contain the Sprint 1 delivery only. See `sprint1-inventory.md` for the inspection/removal record and `sprint1-files.md` for the file manifest.
