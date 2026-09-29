# Sprint 1 record

This document records what Sprint 1 built, how it was tested, and the
deliverables produced. It is kept consistent with the actual implementation
(project rule 12: keep the written design consistent with the application).

## Sprint goal

A working first version where a business owner can create an account, manage a
profile, save a business idea, control its visibility, and receive or update a
saved AI business assessment.

## User stories → implementation → tests (traceability)

| Story | Completion check | Where implemented | Test(s) |
|---|---|---|---|
| **US01** Register / login / logout / session | valid registration creates account; invalid details rejected; duplicate email rejected; valid login opens workspace; invalid login denied; sign-out ends session | `services/auth.py`, `routers/auth.py`, `core/deps.py` | `test_auth.py` (11 tests) |
| **US02** Recover access (single-use, time-limited reset) | valid reset changes password; expired rejected; used cannot be reused; reset secrets not stored as readable text | `services/auth.py`, `routers/auth.py` (tokens stored as SHA-256) | `test_password_reset.py` (8 tests) |
| **US03** Maintain profile | valid changes saved & shown; cannot edit another profile; role cannot be changed via profile update | `routers/profile.py`, `schemas/profile.py` (no role field) | `test_profile.py` (6 tests) |
| **US04** Role-based dashboard | per-role dashboard; role restrictions not bypassed by direct request | `routers/dashboard.py`, `core/deps.py` (`require_business_owner`) | `test_dashboard.py` (7 tests) |
| **US05** Submit & manage idea | required fields checked; connected to owner; reopen & edit; revision increases on assessment-related change; another user cannot edit | `services/business_ideas.py`, `routers/business_ideas.py` | `test_business_ideas.py` (11 tests) |
| **US06** Receive assessment | shows in-progress; valid structure saved; assumptions labeled; failed request shows useful message | `services/assessment.py`, `routers/assessments.py`, `ai/` | `test_assessments.py` (success, failure, invalid-structure) |
| **US07** Refine assessment | new result uses updated idea; idea revision recorded; no duplicate concurrent requests; previous result preserved on failure | `services/assessment.py` (row lock + IN_PROGRESS guard) | `test_assessments.py` (update-after-edit, two-concurrent, previous-preserved) |
| **US08** Control visibility | setting saved; private hidden from others; rule checked by server on every request | `services/business_ideas.py`, `routers/business_ideas.py` | `test_visibility.py` (5 tests) |

**Total: 57 automated tests, all passing.**

## Security rules enforced (section 8 of the guide)

- ✅ Every protected action is checked by the server (`core/deps.py`), not only
  hidden on the screen.
- ✅ Users cannot read or change another user's private records (idea
  visibility + profile visibility; non-owners get 404 for private ideas).
- ✅ Inputs are saved before calling the AI service (the IN_PROGRESS row is
  committed before the AI call).
- ✅ A failed AI request does not delete the last successful result (each
  attempt is its own row; `latest_valid` is preserved).
- ✅ AI assumptions are clearly labeled (the mock provider marks every result
  as simulated; the Gemini prompt requires an explicit assumptions field).
- ✅ Useful, non-technical error messages (validation handler + generic 500
  handler in `main.py`).
- ✅ Responsive on computer and phone-sized screens (Tailwind responsive
  utilities; tested layouts).
- ✅ Keyboard-accessible forms with labels (`Input`/`TextArea`/`Select`
  components associate `<label>` with inputs and set `aria-invalid`).
- ✅ Secret keys outside source code (`.env` is git-ignored; only
  `.env.example` is committed).
- ✅ Only permitted / clearly-labeled fictional data is used for demonstrations
  (the seed script creates fictional Saudi business ideas; survey participants
  are not used as users).

## Screens built (13 required)

1. Registration — `app/register/page.tsx`
2. Login — `app/login/page.tsx`
3. Forgot password — `app/forgot-password/page.tsx`
4. Reset password — `app/reset-password/page.tsx`
5. Profile view & edit — `app/profile/page.tsx`
6. Role-based dashboard — `app/dashboard/page.tsx`
7. Business idea list — `app/ideas/page.tsx`
8. Create business idea — `app/ideas/new/page.tsx`
9. Edit business idea — `app/ideas/[id]/page.tsx` (edit mode)
10. Business idea & assessment workspace — `app/ideas/[id]/page.tsx`
11. Assessment result view — `app/ideas/[id]/page.tsx` (AssessmentPanel)
12. Visibility setting — `app/ideas/[id]/page.tsx` (visibility section)
13. Useful error, loading, empty states — `components/States.tsx` (used on every
    data screen)

## Data model (entity overview)

- `users` — account, role, status, verification status
- `profiles` — one-to-one with user, role-specific info, visibility
- `sessions` — opaque token sessions (only SHA-256 hash stored)
- `password_resets` — single-use, time-limited reset tokens (hash stored)
- `business_ideas` — owner, fields, visibility, revision number
- `assessments` — per-attempt rows; `seq` for deterministic ordering; status
  pending/in_progress/succeeded/failed; the seven required assessment fields

See `backend/app/models/` for the schema and `docs/erd.md` for the diagram.

## Deliverables checklist

- [x] Working software (backend + frontend, running locally)
- [x] Source code in a repository (`git init`)
- [ ] Task board showing owners and status *(GitHub project board — to be
      created by the team; stories US01–US08 mapped above)*
- [x] Sprint goal (this document)
- [x] US01–US08 acceptance criteria (traceability table above)
- [ ] Task assignments *(per the team responsibility model in the guide;
      names/IDs to be filled in by the team)*
- [ ] Updated class / system structure diagram *(to be drawn from the model)*
- [ ] Use case diagram
- [ ] Sequence diagrams for important actions
- [ ] Entity relationship diagram
- [ ] Database schema (the SQLAlchemy models are the source of truth; an ERD
      should be generated from them)
- [ ] Interface prototype updated to match the build
- [x] Test cases with actual results (`backend/tests/`, 57 passing)
- [ ] Bug list with status *(no known critical defects at Sprint 1 close)*
- [ ] Demonstration record and supervisor feedback
- [ ] Sprint review
- [ ] Sprint retrospective
- [ ] Individual contribution table with evidence

The unchecked items are team / documentation artifacts that depend on student
names, IDs, and supervisor review — they are recorded here as outstanding per
the guide's "definition of complete".

## Known limitations

- The AI provider defaults to **mock** (clearly-labeled simulated results) so
  the app runs without an API key. Switch to Gemini by setting
  `AI_PROVIDER=gemini` + `GEMINI_API_KEY` in `backend/.env`.
- Verification flow (US13) and downstream Sprint 2/3 features are intentionally
  out of Sprint 1 scope; the `verification_status` field exists but the flow is
  not built.
- Password reset "email delivery" returns the token in the API response only
  in non-production environments for testing; in production it must be delivered
  by email (the code path is already isolated behind an environment check).
- No Alembic migrations yet; tables are created from the models. Add Alembic
  when the schema starts evolving in Sprint 2.
- Hosting is local only; deployment is a later step (the guide requires a
  deployed version at sprint close — pick a low-cost provider and add
  deployment notes then).

## How to demonstrate Sprint 1

1. Start the stack (see `README.md`).
2. Sign in as `owner1@nashaa.sa` / `Password123!`.
3. Open the dashboard → see GreenBox, FreshBite, WaterWise.
4. Open **GreenBox** → see the saved successful assessment (market, customers,
   competitors, costs, next steps, assumptions, sources).
5. Click **Generate assessment** on an idea without one → watch the in-progress
   state, then the result.
6. **Edit** the idea's problem → revision increases to 2 → regenerate → the new
   assessment records revision 2 (US07).
7. Change **visibility** to Registered → sign in as another owner → the idea
   appears in Browse as a summary only (US08).
8. Sign out → the session ends (US01).
9. Use **Forgot password** → get a demo reset link → reset → log in with the
   new password (US02). Expired/used tokens are rejected (see tests).
