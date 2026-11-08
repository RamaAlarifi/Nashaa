# Sprint 3 validation record

Executed locally on 28 October 2026 against the Project Charter US17-US24 and Nashaa_Guide.md. Fictional development accounts and records were used. This is engineering verification, not a human usability study.

## Executed checks

| Check | Actual result | Limits |
|---|---|---|
| Complete backend regression suite, Python 3.11 container | 197 passed, 0 failed, 0 skipped; 120.57 seconds | Includes 159 previous cases and 38 new Sprint 3/provider cases. Two dependency deprecation warnings; no test failures. |
| Host regression suite following FastAPI/security updates | 197 passed, 0 failed; 249.69 seconds | Host Python 3.10 is not the release runtime. |
| Provider failure-path checks following safe diagnostic logging | 11 passed | HTTP errors, malformed/incomplete responses and timeouts use controlled transports, not live credentials. |
| Frontend TypeScript and unused-code checks | Passed | `npm run check`. |
| Production frontend build | Passed | Next.js 15.5.28; 24 static pages plus dynamic routes. Both release images run as `nashaa`, not root. |
| Chrome production-build system journey | 14 application checks passed; one live outreach generation attempt blocked by HTTP 503 | Explicit test-only manual draft is used after a recorded provider failure. Its editing/copying checks do not establish live generation success. Live customer-profile generation succeeded. |
| Development-browser journey | 14 application checks passed; two live generation attempts blocked by HTTP 503 | These blocked outcomes are retained separately from successful transport and editing tests. No silent provider fallback exists in the application. |
| Live saved-lead outreach retry | HTTP 200 through the actual authenticated application endpoint; provider Gemini | Follow-up after the recorded blocked browser attempt. The previous failed result remains recorded. |
| Live provider diagnostic | HTTP 200; all nine customer-profile fields validated using Gemini | Fictional supplied business context; no external research performed. Availability remains dependent on the provider. |
| Local pilot smoke | 30/30 authenticated lead/collaboration reads succeeded at concurrency 5; p95 2.722 seconds | Local measurement through the production frontend. The team has not supplied an agreed load/capacity target. |
| Migration | Application database at `0007_sprint3` | Regression suite checks preservation of prior sprint records and disposable downgrade/upgrade. |
| Backup and isolated restore | Passed | Schema version and all selected S1-S3 table counts matched. Application database was not replaced. Evaluation records remained zero. |
| npm dependency audit | Zero known vulnerabilities | Patched Next.js and affected transitive lockfile dependencies. |
| Release Python package audit | Zero known vulnerabilities in the image package inventory | Python 3.11 permits patched dnspython 2.9.0. FastAPI, Starlette, multipart, dotenv, certificates and packaging tooling updated. This is not an OS-layer vulnerability scan. |
| Docker Scout OS/image scan | Blocked | Docker ID authentication is required and is not configured. No claim of a clean operating-system image scan is made. |

## Coverage and defects corrected

The acceptance tests cover collaborator membership and completion authority; generated and owner-edited customer profiles; concurrent-edit preservation; validated whole-file imports and provenance; consumer segments; private customer/investor leads, duplicate saves, notes and statuses; draft editing and failure preservation; completed-work ratings; reports and inspection; atomic administration/audit actions; account-session invalidation; hidden-content boundaries; and empty/actual evaluation aggregation.

The browser journey uses owner, innovator, investor and administrator accounts. It exercises saved results, invalid CSV feedback, challenge proposal/selection, progress, completion, both ratings, reporting and administrative decisions/actions. Mobile width (390 px), keyboard focus and absence of browser runtime errors are checked. This is not a full accessibility or cross-browser certification.

A real form defect was corrected during browser testing: shared ActionForm instances produced duplicate field IDs. React useId now provides unique label/control associations. Outreach copy state is also refreshed after generation/save and disabled while a draft action is pending. Earlier browser-script strict-selector failures caused by repeated fictional records were corrected without removing application checks.

Provider failures return understandable errors and preserve prior saved work. Sanitised diagnostics record HTTP status or exception type without logging keys, prompts, plan contents or generated text. Live generation can fail intermittently; a successful retry does not erase a failed earlier attempt.

## Evidence

Evidence is stored outside source control in the Codex workspace `work/sprint3`: `container-tests.xml`, `full-tests.xml`, `browser/results.json`, `release-browser/results.json`, screenshot PNGs, `pilot-smoke.json`, `runtime-requirements.txt`, `runtime-audit.json`, `live-outreach-retry.json` and `backup-final.dump`. The archive contains application data and must remain private. Earlier diagnostic runs are not substituted for the final recorded outcomes.

The backup comparison covered users, ideas, assessments, collaborations, customer profiles, leads, ratings, reports, audit actions, progress updates, lead sources, company records, notes, drafts and evaluation sessions. Its verified snapshot includes completed work and ratings. It predates subsequent fictional release-browser records.

## Remaining completion evidence

- External hosting, HTTPS termination and real SMTP delivery are not configured or exercised here. Production Compose and configuration checks support deployment; they do not establish that deployment occurred.
- Docker container recreation/health recovery is verified; host-reboot recovery is not.
- Actual consenting participants, reviewed recommendation/assessment samples and satisfaction responses are still required for charter KPI evaluation. The evidence dashboard deliberately reports unevaluated measures when observations are absent.
- The team must identify the agreed pilot workload and additional supported browsers before capacity and browser-coverage acceptance can be certified.
- Final supervisor review, team contribution statements, academic report and presentation require real team input. No feedback or experiences have been invented.

All eight Sprint 3 stories have implemented workflows and automated acceptance coverage. Provider availability and the external deployment/evaluation deliverables above remain explicit limitations; the entire charter is not declared complete.
