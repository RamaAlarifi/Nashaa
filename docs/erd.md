# Entity Relationship Diagram (Sprint 1)

Generated from the SQLAlchemy models in `backend/app/models/`. This is the
authoritative schema; the code is the source of truth.

```
┌──────────────────────────┐       1:1       ┌──────────────────────────┐
│ users                   │─────────────────▶│ profiles                 │
│─────────────────────────│                  │─────────────────────────│
│ id (UUID, PK)           │                  │ id (UUID, PK)           │
│ email (unique)          │                  │ user_id (FK→users.id)   │
│ password_hash           │                  │ display_name            │
│ role (enum)             │                  │ location                │
│ account_status (enum)   │                  │ short_description        │
│ verification_status     │                  │ role_specific_info(JSONB)│
│ created_at, updated_at  │                  │ contact_preference(enum)│
└────────────┬─────────────┘                  │ profile_visibility(enum)│
             │                                │ created_at, updated_at  │
             │ 1:N                            └──────────────────────────┘
             │
      ┌──────┴─────────────────────┐
      ▼                            ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│ sessions                │   │ business_ideas            │
│─────────────────────────│   │─────────────────────────│
│ id (UUID, PK)           │   │ id (UUID, PK)            │
│ user_id (FK→users.id)   │   │ owner_id (FK→users.id)   │
│ token_hash (unique)     │   │ name                     │
│ expires_at              │   │ problem, solution        │
│ created_at              │   │ industry                 │
└──────────────────────────┘   │ business_stage(enum)     │
                               │ target_location          │
┌──────────────────────────┐   │ intended_customers       │
│ password_resets          │   │ budget                   │
│─────────────────────────│   │ current_challenges       │
│ id (UUID, PK)           │   │ visibility(enum)         │
│ user_id (FK→users.id)   │   │ revision_number(int)      │
│ token_hash (unique)     │   │ created_at, updated_at   │
│ expires_at              │   └────────────┬─────────────┘
│ used_at (nullable)      │                │ 1:N
│ created_at              │                ▼
└──────────────────────────┘   ┌──────────────────────────┐
                               │ assessments               │
                               │─────────────────────────│
                               │ id (UUID, PK)            │
                               │ idea_id (FK→business_ideas.id)│
                               │ seq (IDENTITY, ordering) │
                               │ idea_revision(int)        │
                               │ input_snapshot(JSONB)    │
                               │ market_considerations     │
                               │ target_customer_analysis │
                               │ competitor_considerations│
                               │ indicative_costs         │
                               │ suggested_next_steps     │
                               │ assumptions              │
                               │ sources                  │
                               │ generation_status(enum)  │
                               │ error_message(nullable)  │
                               │ created_at, updated_at   │
                               └──────────────────────────┘
```

## Relationships

- `users` 1:1 `profiles` (a profile is created at registration)
- `users` 1:N `sessions` (opaque token sessions; deleted on logout/expiry)
- `users` 1:N `password_resets` (single-use, time-limited)
- `users` 1:N `business_ideas` (owner)
- `business_ideas` 1:N `assessments` (one row per attempt; `latest_valid` =
  most recent SUCCEEDED)

## Enums

- `Role`: business_owner, innovator, investor, admin
- `AccountStatus`: active, suspended, deactivated
- `VerificationStatus`: unverified, pending, verified, rejected
- `BusinessStage`: idea, validation, early, operating, scaling
- `IdeaVisibility`: private, registered
- `ProfileVisibility`: public, registered, private
- `ContactPreference`: direct_message, contact_request
- `AssessmentStatus`: pending, in_progress, succeeded, failed

## Notes

- Enumerations are stored as `VARCHAR` (`native_enum=False`) to keep schema
  changes simple across sprints.
- Password hashes use bcrypt (`passlib`); session/reset tokens are stored only
  as SHA-256 hashes — the plaintext is never persisted.
- `assessments.seq` is a database `IDENTITY` sequence so attempts order
  deterministically even within a single transaction (where `now()` is
  constant).
