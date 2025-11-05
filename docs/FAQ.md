# Tenantra — Frequently Asked Questions (FAQ)

## Authentication & Access Control
- Sign in at `/login`. Default dev admin is `admin` / `Admin@1234` (seeded). JWTs are issued by `POST /auth/login`. Inspect the current user via `GET /auth/me`. Admins can manage users and settings.

## Tenants & CORS
- CORS can be set via Admin Settings and by creating `TenantCORSOrigin` records. The backend can infer tenant from subdomain or `X-Tenant-Id` / `X-Tenant-Slug` headers.

## Admin Settings
- Global: `PUT /admin/settings` with `{ key: value }` pairs.
- Tenant: `PUT /admin/settings/tenant` scoped to the admin’s tenant.
- Useful keys:
  - `grafana.url` for UI links to Grafana.
  - `integrity.registry.ignore_prefixes`: array or comma string of key path prefixes.
  - `integrity.service.ignore_names`: service names to ignore.
  - `integrity.service.ignore_names.agent.<id>`: per‑agent service ignores.
  - `integrity.alert.email.to`: recipients for critical drift (string or array).

## Modules & Execution
- View and run modules from `/app/modules`. Programmatic runs via `POST /module-runs/{id}`. Scheduling available via `/schedules`; enable the scheduler worker with `TENANTRA_ENABLE_MODULE_SCHEDULER=1`.

## Notifications
- Create via `POST /notifications`. See history at `/notification-history` and settings at `/notifications/settings`. Critical integrity drift will queue notifications to recipients defined in `integrity.alert.email.to` (tenant setting).

## Compliance
- Results: `/compliance/results`, trends: `/compliance/trends`, exports: `/compliance/export.csv` and `/compliance/export.pdf`. Frontend includes Trends and Matrix views.

## Observability & Dashboards
- Metrics at `/metrics`. Key integrity metrics:
  - `integrity_ingested_rows{kind}` (registry/service/task/boot)
  - `integrity_drift_events{kind,severity}` (registry/service)
  - `integrity_last_ingest_timestamp{kind}` (gauge)
- Grafana dashboards auto‑provisioned in `docker/grafana-provisioning/dashboards/`.

## Process Monitoring & Drift
- Under `/app/process-monitoring`, load agent snapshot, seed and save baselines, and view drift events. API supports baseline CRUD and snapshot ingestion.

## Integrity (Registry, Services, Tasks, Boot)
- Ingestion endpoints:
  - Registry: `POST /integrity/registry` (supports `full_sync=true` for removal detection)
  - Services: `POST /integrity/services`
  - Tasks: `POST /integrity/tasks` (supports `full_sync=true` for missing checks)
  - Boot: `POST /integrity/boot`
- Baselines:
  - Services: `GET/POST /integrity/services/baseline`
  - Registry: `GET/POST /integrity/registry/baseline`
  - Tasks: `GET/POST /integrity/tasks/baseline`
  - Scope: tenant defaults and per‑agent overrides.
- Ignore controls (tenant):
  - `integrity.registry.ignore_prefixes`, `integrity.service.ignore_names`, `integrity.service.ignore_names.agent.<id>`
- Severity policy:
  - Services: Disabled→Auto elevates to high; unsigned `.sys` with missing/changed hash elevates to critical.
  - Registry: add/change/removal becomes critical when a matching baseline is marked critical.
  - Tasks: change or full‑sync missing becomes critical when the baseline is marked critical.
- Diff endpoints:
  - Services: `/integrity/services/diff?agent_id=&left=&right=`
  - Registry: `/integrity/registry/diff?agent_id=&hive=&left=&right=`
- Alerts:
  - Critical service and registry drift queue notifications to recipients from `integrity.alert.email.to`. Worker delivers via SMTP.
- Integrity UI (`/app/integrity`):
  - Scope (tenant/agent), agent ID, filters, refresh.
  - Editors: service/registry/task baselines; registry ignores; tenant and agent service ignores.
  - Diff controls and JSON results panels.
  - Events table with type and severity filters.
  - Baseline mismatch highlighting in runtime lists.

## Dev & CI
- Dev stacks documented in `docs/DEV_STACKS.md` (MailHog, Observability, Scheduler, all‑in‑one up/down scripts).
- OpenAPI snapshot regen: `backend/tools/generate_openapi.py`; CI freshness gate in backend workflow.
- API E2E: Postman collection and environment under `postman/`, with runner scripts.
- Backend Deep Audit: `tools/phase8_deep_audit.py` and optional workflow.
- UI smoke: Playwright test suites in `frontend/tests/e2e/`.

## Retention & Cleanup
- Default retention is 30 days per tenant; override with `tenant_retention_policies.integrity_days`.
- Cleanup script `backend/scripts/cleanup_integrity.py` supports flags:
  - `--days`, `--tenant`, `--cutoff`
- Nightly cleanup workflow: `.github/workflows/integrity-cleanup.yml` runs at 03:00 UTC.

## SMTP & MailHog
- Configure via `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `SMTP_TLS`.
- Development overlay includes MailHog (SMTP 1025, UI 8025).

## Troubleshooting
- 401 on protected routes: sign in; confirm `Authorization: Bearer <token>` header.
- CORS rejections: configure allowed origins in Admin Settings or DB.
- No integrity data: run collectors; confirm scheduler/worker flags.
- Empty exports: run runners to generate compliance results.

## Common Issues
- Observability 404: ensure `grafana.url` is set and Grafana is reachable from backend container.
- Grafana 401/403: set `GRAFANA_USER` and `GRAFANA_PASS` env vars for backend.
- Modules list empty: run DB seed inside backend container; ensure `/app/docs/modules/Tenantra_Module_Backlog_PhaseLinked_v8.csv` is present (mapped from repo `docs/modules`).
- API 401 on admin routes: ensure you are authenticated with a valid bearer token (admin role).
