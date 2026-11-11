# Sprint 3 implementation and requirement traceability

The Project Charter is the scope and acceptance baseline. Nashaa_Guide.md sections 8, 13 and 25 guide implementation. Existing Next.js, FastAPI, PostgreSQL, SQLAlchemy and Alembic conventions are retained. Existing application libraries are reused, with security updates to the release dependencies. The release backend uses Python 3.11 to support patched dnspython.

## Scope and implementation map

| Charter story and requirements | Implementation and dependency | Acceptance verification |
|---|---|---|
| US17 / FR10: collaborative progress and completion | Existing selected Collaboration receives active, ready and completed states. Both participants can add progress. Only the selected innovator marks ready; only the owner confirms completion. State changes lock the collaboration row. `/collaborations` and its detail workspace build on Sprint 2 selection. | `test_us17_us22_complete_journey_and_privacy`, browser publication-to-completion journey. |
| US18 / FR16: generate and refine target customers | Owner-only customer workspace linked to the saved idea; business/consumer focus, editable customer type, industry, location, size, need, motivation, objections, channels and assumptions. OpenAI receives the submitted plan and category catalogue. Saved profile edits are used by subsequent suggestions. Revision and intervening-edit checks prevent stale generated content overwriting saved changes. | `test_us18_generate_refine_private_saved_profile`, generation-failure and intervening-owner-edit tests, real-browser generation/editing. |
| US19 / FR17: permitted business leads and consumer suggestions | Owner-attested CSV imports record source, permission, filename and fictional status. Whole-file validation precedes persistence. Exact headers, 100 KB/200-row limits, canonical categories, safe URLs and formula/control-character rejection apply. Matching explains industry, location and stated-need overlap. Consumer focus returns segment/channel hypotheses, never personal contacts. | Import validation and atomicity cases; consumer-segment case; source/duplicate checks; browser invalid/valid import. |
| US20 / FR18: editable outreach | Server-side OpenAI generation combines saved business context and the selected saved lead. Drafts can be edited, saved and copied. No send endpoint or automatic communication is introduced. Errors preserve leads, notes and the previous draft. | Draft context/edit/failure case, transport failures and browser edit/save/copy. |
| US21 / FR19: private lead follow-up | Both customer records and suggested investors can be saved for an owned idea. A database uniqueness constraint and idea lock handle repeated saves. Eight follow-up statuses and append-only private notes persist. Saved snapshots retain provenance when discovery inputs change. | Source/duplicates/follow-up test, investor-lead test and owner/outsider boundaries; browser reopening. |
| US22 / FR20: completed-work ratings | Membership and completed state are checked on the server. Scores are 1-5. Unique author/collaboration pairs prevent duplicate ratings. Recipient derives from the collaboration, never client input. Publicly visible profiles expose only aggregate reputation; raw comments remain in the participant workspace. | Completed-work journey, score/spoofing boundaries and duplicate rejection; browser ratings from both roles. |
| US23 / FR21: issue reporting | Report forms on profiles, ideas, challenges, collaborations and messages capture category, related record and description. Access to the target is checked before recording the report. Reporters see confirmation and their own report decisions. | Report-to-admin journey; private/unknown target rejection; own-report scoping. |
| US24 / FR22: administration | Admin queue, reported-record inspection, reasoned resolution/dismissal, participant suspension/reactivation/deactivation, content hiding/restoration and message removal. Administrator accounts cannot be suspended here. Suspension/deactivation invalidates sessions. Report decisions and actions commit atomically with audit records. Verification decisions are also audited. Activity summaries are count-based. | Moderation/audit, session invalidation and admin protection tests; direct role checks; browser report decisions. |

## Engineering decisions

- Selection remains the Sprint 2 operation: the challenge closes while a separate collaboration begins as active. Completion does not reopen the challenge or alter the selected proposal.
- Customer-profile kind is explicitly chosen by the owner. Target-customer industry can differ from the business's own industry. Both use the established catalogue.
- The project includes no licensed external lead dataset. Company discovery therefore uses permission-confirmed uploads. Consumer segments are hypotheses from the saved customer profile, not validated demand.
- Import duplicates are identified by case-insensitive company name and location within the idea. Re-import does not silently overwrite an existing source record. Saved lead snapshots preserve their original source.
- Customer scoring is deterministic: industry 50, location 30, overlapping stated-need terms 20. A nonzero result is a possible fit, with displayed reasons/missing data; it is not verified demand. Human relevance evaluation remains necessary.
- AI calls remain server-only. Real-provider failures never silently fall back to simulated generation. Mock mode is used by isolated tests; its UI output is labelled. Generation uses no browsing or external verification.
- Content moderation is a separate server-owned flag. Owner edits and registered visibility cannot undo an administrator's hide action. Hidden ideas are removed from public browsing, matching, assessment sharing and contact eligibility; hidden challenges cannot be discovered, submitted to or published. Existing owners retain their own records.
- Reports do not give ordinary users new access to private content. Administrative inspection is limited to the reported record and is logged. Account records never expose password/session data through moderation.
- CSV upload is bounded JSON text, avoiding another file-processing dependency or container-local upload store. Imported records and provenance are persisted in PostgreSQL.
- Evaluation recording requires administrator access, anonymous participant codes and an explicit consent confirmation. Empty datasets return null metrics, not invented results. Investor/customer top-five relevance is calculated separately with reported denominators and role/browser coverage.

## Data and migration

Apply `0007_sprint3` with `docker compose exec -T backend alembic upgrade head`. The migration preserves prior records, defaults existing collaborations to active, adds moderation flags, and creates progress, customer-profile, source/company, lead/note, draft, rating, report, audit and evaluation tables. Downgrade removes Sprint 3 records and must only be exercised on a disposable database. The regression suite upgrades actual Sprint 1-shaped records, compares the resulting metadata, and tests downgrade/upgrade preservation.

Explicit development-only examples: `docker compose exec -T backend python -m app.seed.sprint3`. Accounts are `s3-owner@example.com`, `s3-innovator@example.com`, `s3-investor@example.com` and `s3-admin@example.com`, using the documented local demo password `Password123!`. All records are labelled fictional. No evaluation observations are seeded. The seed command refuses non-development environments.

## Verification commands

Backend: use Python 3.11 for the release environment. From `backend`, run `.venv\Scripts\python.exe -m pytest -c pytest-sprint2.ini -q -p no:cacheprovider`.

Frontend static check: `docker compose exec -T frontend npm run check`.

Browser: from `frontend`, run `node e2e/sprint3.cjs` with Playwright resolvable, Chrome installed, running local services and explicit fictional Sprint 3 seed data. Optional `NASHAA_E2E_BASE`, `NASHAA_E2E_OUTPUT`, `NASHAA_PLAYWRIGHT_MODULE` and `NASHAA_BROWSER_CHANNEL` control execution. The test records live AI failures as Blocked rather than manufacturing successful results.

Backup verification: from the repository root, run `powershell -NoProfile -File scripts/backup-restore.ps1 -BackupFile .backups\sprint3.dump -VerifyRestore`. It creates a new archive outside the container, restores into a uniquely named disposable database, compares schema/key table counts, and removes only that test database. It never replaces the application database and never overwrites an existing backup. Backups contain private data and must stay outside source control with restricted access and a team-approved retention policy.

## Final delivery boundaries

See `sprint3-validation.md` for executed results. Local tests and generated screenshots are engineering evidence, not user evaluation. The charter's human task-completion, recommendation relevance, assessment-quality and satisfaction targets require actual consenting participants and reviewed samples. Production HTTPS, real SMTP delivery, hosting credentials, host-reboot recovery and external supervisor/team deliverables cannot be certified from a local container test. No team contributions or supervisor feedback are invented.
