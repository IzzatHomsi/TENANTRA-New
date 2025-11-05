# Tenantra Platform AI Agent Instructions

Below are concise, repo-specific notes to help an AI agent be productive when editing, testing, and extending Tenantra.

## High-level architecture (what to keep in mind)
...
## Concrete examples of tenant-aware patterns
...
## Small gotchas and tips (observed)
...
## When adding endpoints or changing tenant behavior
...
- Many helper scripts assume execution from repo root or inside the backend container. Prefer `make` targets or `tools/` PowerShell wrappers to avoid path issues.
 # Tenantra Platform AI Agent Instructions (detailed)

This document captures repository-observed conventions, useful commands, and concrete examples that help an AI agent or reviewer be productive in this codebase.

## Big-picture architecture
- Backend: FastAPI application lives in `backend/app`. App entry is `app.main:app` (see `backend/Dockerfile` which starts `uvicorn app.main:app`). Logging is bootstrapped in `backend/app/main.py` and supports a project logging module `app/logging_conf`.
- Database: PostgreSQL via SQLAlchemy. Migrations live under `backend/alembic`. The repo includes helper scripts such as `tools/verify_alembic_single_head.py`, `tools/phase8_deep_audit.py` and other validators in `tools/`.
- Frontend: Vite-based SPA in `frontend/`. Playwright E2E tests in `tests/e2e/` (and `tests/smoke/`) use real endpoints and JWTs.
- Orchestration: Docker Compose with multiple overlays in `docker/` (health, worker, nginx). `Makefile` provides convenient compose wrappers: `make up`, `make migrate`, `make seed`, `make test`.

## Exact developer commands & common flows
- Start dev stack (default override):
```pwsh
make up
```
- Apply DB migrations:
```pwsh
make migrate
# or: docker compose exec -T backend alembic upgrade head
```
- Seed default tenant, admin user, and dev CORS origin:
```pwsh
make seed
# runs: python scripts/db_seed.py inside backend
```
- Run backend tests inside container:
```pwsh
make test
```
- Run Playwright E2E locally (install deps first):
```pwsh
npm run e2e:init
npm run e2e:smoke
```

## Key repository conventions (concrete)

- Tenant resolution: Endpoints must resolve tenant context. Supported inputs:
   - Query param: `?tenant_id=...`
   - Header: `X-Tenant-Slug` (used by validators and tests). See `tests/e2e/cors.spec.ts` and `tools/validate_tenantra.py`.

- Tenant-scoped CORS: Origins are stored per-tenant (model `TenantCORSOrigin` under `backend/app/models`). `backend/scripts/db_seed.py` seeds `http://localhost` for the default tenant to support local dev. Playwright and validators verify CORS preflight behavior.

- Seeding pattern: Seeders use idempotent pattern — query-by-tenant/role then insert-if-missing. Follow this pattern for new seeders (see `backend/scripts/db_seed.py`).

- Auth & tokens: JWT-based auth. Env-controlled values (see `DEPLOY.md`) include `JWT_SECRET`, `JWT_ALG`, `JWT_EXPIRE_MINUTES`. Token helpers are in `backend/app/core/security.py`.

- Alembic hygiene: CI enforces a single alembic head. Run `tools/verify_alembic_single_head.py` locally and merge heads with `alembic merge` if needed.

## Environment variables and defaults (observed)
- Database: `DATABASE_URL` (example: postgresql+psycopg2://user:pass@db:5432/tenantra)
- CORS and modes: `CORS_ALLOWED_ORIGINS`, `CORS_MODE`
- JWT and auth: `JWT_SECRET`, `JWT_ALG`, `JWT_EXPIRE_MINUTES`
- Test helpers & validators: `TENANTRA_TEST_TENANT_SLUG`, `TENANTRA_API`, `TENANTRA_NGINX`, `TENANTRA_GRAFANA`, `TENANTRA_VALIDATE_GRAFANA`, `TENANTRA_API_TOKEN`
- Frontend/E2E: `E2E_BASE_URL` (see `tests/utils/testEnv.ts` defaults to `https://Tenantra.homsi-co.com`)

Set these in your `.env` or in the environment when running local compose or validators.

## Testing, validators & how to run them
- Unit / integration: `make test` executes pytest in the backend container.
- E2E: Playwright tests live under `tests/e2e/` and `tests/smoke/`. They require a running stack and correct env (e.g., `TENANTRA_TEST_TENANT_SLUG`).
- Validators: `tools/validate_tenantra.py` and `tools/validate_tenantra_phases.py` run deterministic checks (OpenAPI presence, roles, CORS preflight, seeding). They expect services to be running and may call external services (Grafana, Nginx) depending on env.
- Quick runner scripts (added):
   - `tools/run_all_validations.sh` — Unix wrapper that runs alembic check + validators (creates `tools/reports` output).
   - `tools/run_all_validations.ps1` — PowerShell wrapper for Windows.

Note: validators may call `alembic` or `docker` — run them in an environment with those tools installed or from inside the backend container.

## Deployment and overlays
- Overlays in `docker/`: examples include `docker-compose.override.health.yml`, `docker-compose.override.worker.yml`, `docker-compose.override.nginx.prod.yml` and staging variants. Use `-f` flags to combine.
- Post-migration: always run `alembic upgrade head` inside the backend container as a post-deploy step (CI and `DEPLOY.md` follow this).

## Files to inspect when changing behavior
- App init & logging: `backend/app/main.py` (logging bootstrap and app factory)
- Models: `backend/app/models/*` (Tenant, TenantCORSOrigin, Role, User, AppSetting)
- DB seeders: `backend/scripts/db_seed.py` (idempotent seeder pattern)
- Validators & audit: `tools/validate_tenantra.py`, `tools/validate_tenantra_phases.py`, `tools/phase8_deep_audit.py`
- Compose overlays: `docker/` directory and `Makefile` (Compose selection with `DEV` flag)
- Playwright tests and test helpers: `tests/e2e/`, `tests/smoke/`, `tests/utils/testEnv.ts`

## Concrete tenant-aware examples to copy
- CORS preflight (Playwright): OPTIONS to `/api/auth/login` with headers `Origin` and `X-Tenant-Slug` should return 204 and echo `Access-Control-Allow-Origin` and `Access-Control-Allow-Credentials: true` (see `tests/e2e/cors.spec.ts`).
- Idempotent seeding: check `backend/scripts/db_seed.py` for the pattern: query existing row (tenant/role) then insert only if missing.

## PR reviewer checklist (new file)
- See `.github/PR_REVIEW_CHECKLIST.md` — use it when reviewing PRs that touch migrations, seeds, tenant behavior, or CORS. It lists exact steps (alembic single-head, seed idempotency, tenant header checks, tests updated).

## Small gotchas and tips (observed)
- Many helper scripts assume execution from the repo root or inside the backend container. Use `Makefile` targets or the PowerShell wrappers in `tools/` to avoid path issues.
- Alembic head conflicts are enforced by CI — run `tools/verify_alembic_single_head.py` before opening migration PRs.
- Validators reference environment variables for Grafana/Nginx/GitHub-aspects — set `TENANTRA_GRAFANA`, `TENANTRA_NGINX`, and related env vars before running full validators.

## Suggested follow-ups (I can implement)
- Add a GitHub PR template that embeds the PR reviewer checklist automatically.
- Make `tools/run_all_validations.sh` strict (exit non-zero if validators fail) for CI usage.
- Add a small example endpoint that demonstrates the recommended pattern to resolve `X-Tenant-Slug` → tenant id (and include unit + e2e tests).

If you want one of these, tell me which and I'll implement it.
