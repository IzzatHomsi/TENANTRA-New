
# Tenant-aware CORS

This patch enables CORS to be controlled centrally from the database. Admins can register allowed origins per tenant.
- Safe default: no origin is allowed unless added to env or DB.
- Preflight (OPTIONS) handled by middleware; successful origins receive proper CORS headers.

## Admin API
- `GET /admin/cors` — list all (optional `?tenant_id=`)
- `POST /admin/cors` — `{ "tenant_id": 1, "origin": "https://app.example.com", "is_global": false }`
- `PATCH /admin/cors/{id}` — toggle `enabled`, `is_global`, or change `origin`
- `DELETE /admin/cors/{id}` — remove

## Behavior
- If `CORS_ALLOWED_ORIGINS` env is set, those are always allowed.
- DB entries allow additional origins; `enabled=false` disables without deleting.
- `is_global=true` is informational here (future use for non-tenant-bound flows).

## Migration
Run `alembic upgrade head` after applying files.

## Running locally

```bash
make up       # start the stack
make migrate  # apply migrations
make seed     # bootstrap default admin/roles
```

Visit `http://localhost:5173` for the frontend and `http://localhost:5000/health` for the backend health check. Use `make down` to stop the services.

## CI/CD quick reference

- `backend-ci` runs linting, type checking, security scan and pytest against Postgres.
- `frontend-ci` installs dependencies, runs ESLint and builds the Vite bundle.
- `compose-yaml-lint` validates docker compose manifests and performs `yamllint`.
- `secret-scan` uses gitleaks to guard against credential leaks.
- `deploy-staging` (push to `main`) SSHes into HO-Docker-22, updates the repo, rebuilds containers, migrates + seeds, and runs health probes.
- `post-deploy-probes` performs HTTPS smoke tests against `https://tenantra.homsi-co.com`.

See `DEPLOY.md` for full instructions and required GitHub secrets.

## CI Status
- API E2E (Newman): [![Newman E2E](https://github.com/tenantra/tenantra-platform/actions/workflows/newman-e2e.yml/badge.svg)](https://github.com/tenantra/tenantra-platform/actions/workflows/newman-e2e.yml)
- Backend Deep Audit: [![Deep Audit](https://github.com/tenantra/tenantra-platform/actions/workflows/deep-audit.yml/badge.svg)](https://github.com/tenantra/tenantra-platform/actions/workflows/deep-audit.yml)
- UI Smoke (Process Monitoring): [![UI Smoke](https://github.com/tenantra/tenantra-platform/actions/workflows/playwright-ui.yml/badge.svg)](https://github.com/tenantra/tenantra-platform/actions/workflows/playwright-ui.yml)

## OpenAPI snapshot (new)
- Regenerate snapshot with: `make openapi` or `python backend/tools/generate_openapi.py --output openapi.json`
- CI enforces freshness: backend CI generates `openapi.generated.json` and fails if it differs.

## Feature flags
- Panorama drift stub (Phase 3 prototype): set `TENANTRA_ENABLE_PANORAMA_STUB=true` to enable stubbed success; otherwise runs as `skipped`.
 - AWS IAM live check (Phase 2 prototype): set `TENANTRA_ENABLE_AWS_LIVE=true` and provide AWS creds + `boto3` to attempt live IAM evaluation (falls back to `skipped` if unavailable).

See `docs/FEATURE_FLAGS_SMTP.md` for full details and MailHog dev overlay.

## Dev Stacks
- Combined dev stacks and scripts are documented in `docs/DEV_STACKS.md`.
# TENANTRA-New
