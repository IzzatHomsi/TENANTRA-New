# PR Reviewer Checklist — Tenantra Platform

Use this checklist when reviewing changes that touch backend, DB, migrations, or tenant behavior.

1. Alembic & Migrations
   - [ ] Run `python tools/verify_alembic_single_head.py` (or the CI check) and confirm a single alembic head.
   - [ ] If migrations were added, confirm an idempotent `upgrade` path and no accidental data-loss statements in the migration.

2. Seeds & Data
   - [ ] If the change requires a seeded value (tenant, role, CORS origin), confirm `backend/scripts/db_seed.py` or add a new seeder under `backend/scripts/`.
   - [ ] Verify seeds are idempotent (query-by-tenant then insert-if-missing).

3. Tenant-awareness
   - [ ] Confirm all new endpoints or changed endpoints respect tenant context via `tenant_id` query or `X-Tenant-Slug` header.
   - [ ] If CORS or origin handling changed, add/adjust Playwright test under `tests/e2e/` and/or validator in `tools/`.

4. Tests & Validators
   - [ ] Unit/integration tests added or updated for changed behavior.
   - [ ] E2E tests updated if UI or HTTP contract changed (see `tests/e2e/`).
   - [ ] Run `tools/run_all_validations.sh` (or PowerShell variant) locally to confirm validators pass.

5. Security & Secrets
   - [ ] No secrets or JWT keys committed in code or test fixtures. Use env-based secrets (see `DEPLOY.md`).

6. Logging & Observability
   - [ ] Significant app-level errors are logged using existing structured logging conventions (see `backend/app/main.py` and `app/logging_conf` if present).

7. Documentation & Deploy
   - [ ] Update `DEPLOY.md` if new env vars are required.
   - [ ] Add notes to `.github/copilot-instructions.md` if the change introduces new developer workflows.

Optional: for migrations reviewers
- Run `docker compose up --build -d` and `docker compose exec -T backend alembic upgrade head` in an isolated environment to verify migrations apply.