# Tenantra End‑User Manual (Phases 0→9)

> **Source:** Auto‑generated strictly from Phase 9 repo snapshot. Facts only. Unknowns are marked clearly.

## Introduction

Tenantra is an IT discovery, compliance, and monitoring platform. Up to Phase 9, the system includes authentication, RBAC, core inventory, scanning, notifications, compliance logging, and observability.

## Global Setup & Prerequisites

### Environment Keys

| Env Key | Purpose (from code) |
|---------|----------------------|
| ACCESS_TOKEN_EXPIRE_MINUTES | Unknown (needs source) |
| ADMIN_PASS | Unknown (needs source) |
| ADMIN_USER | Unknown (needs source) |
| APP_VERSION | Unknown (needs source) |
| BACKEND_URL | Unknown (needs source) |
| BASE_URL | Unknown (needs source) |
| CORS_ALLOWED_HEADERS | Unknown (needs source) |
| CORS_ALLOWED_METHODS | Unknown (needs source) |
| CORS_ALLOWED_ORIGINS | Unknown (needs source) |
| CORS_ALLOW_CREDENTIALS | Unknown (needs source) |
| CORS_DB_CACHE_TTL | Unknown (needs source) |
| CORS_MAX_AGE | Unknown (needs source) |
| DATABASE_URL | Unknown (needs source) |
| DB_HOST | Unknown (needs source) |
| DB_PORT | Unknown (needs source) |
| DB_URL | Unknown (needs source) |
| FRONTEND_PATH | Unknown (needs source) |
| FRONTEND_URL | Unknown (needs source) |
| JWT_ALGORITHM | Unknown (needs source) |
| JWT_SECRET | Unknown (needs source) |
| JWT_SECRET_KEY | Unknown (needs source) |
| LOG_DIR | Unknown (needs source) |
| LOG_FORMAT | Unknown (needs source) |
| LOG_LEVEL | Unknown (needs source) |
| OBS_SQL_PROFILER | Unknown (needs source) |
| POSTGRES_DATABASE | Unknown (needs source) |
| POSTGRES_DB | Unknown (needs source) |
| POSTGRES_DBNAME | Unknown (needs source) |
| POSTGRES_HOST | Unknown (needs source) |
| POSTGRES_PASSWORD | Unknown (needs source) |
| POSTGRES_PORT | Unknown (needs source) |
| POSTGRES_USER | Unknown (needs source) |
| RATE_LIMIT_DEFAULT | Unknown (needs source) |
| RATE_LIMIT_OVERRIDES | Unknown (needs source) |
| RATE_LIMIT_WINDOW | Unknown (needs source) |
| REFRESH_IN_COOKIE | Unknown (needs source) |
| REFRESH_TOKEN_EXPIRE_DAYS | Unknown (needs source) |
| SEC_COEP | Unknown (needs source) |
| SEC_CONTENT_TYPE_OPTIONS | Unknown (needs source) |
| SEC_COOP | Unknown (needs source) |
| SEC_CSP | Unknown (needs source) |
| SEC_FORCE_HSTS | Unknown (needs source) |
| SEC_FRAME_OPTIONS | Unknown (needs source) |
| SEC_HSTS | Unknown (needs source) |
| SEC_REFERRER_POLICY | Unknown (needs source) |
| SEED_ADMIN_EMAIL | Unknown (needs source) |
| SEED_ADMIN_PASSWORD | Unknown (needs source) |
| SEED_ADMIN_ROLE | Unknown (needs source) |
| SEED_ADMIN_TENANT_ID | Unknown (needs source) |
| SEED_ADMIN_USERNAME | Unknown (needs source) |
| SEED_TENANT_NAME | Unknown (needs source) |
| SEED_TENANT_SLUG | Unknown (needs source) |
| SLOW_SQL_MS | Unknown (needs source) |
| SMTP_FROM | Unknown (needs source) |
| SMTP_HOST | Unknown (needs source) |
| SMTP_PASS | Unknown (needs source) |
| SMTP_PORT | Unknown (needs source) |
| SMTP_TLS | Unknown (needs source) |
| SMTP_USER | Unknown (needs source) |
| TENANTRA_DEV_CORS_DEFAULT | Unknown (needs source) |
| TENANTRA_ENABLE_NOTIFICATIONS_WORKER | Unknown (needs source) |
| TENANTRA_ENC_KEY | Unknown (needs source) |
| TENANTRA_EXPORT_RATE_MAX | Unknown (needs source) |
| TENANTRA_EXPORT_RATE_WINDOW_SECONDS | Unknown (needs source) |
| TENANTRA_METRIC_LATENCY_BUCKETS | Unknown (needs source) |
| TENANT_NAME | Unknown (needs source) |


### Database Migrations & Seeds

- Alembic migration files: 0

- Seed scripts: backend\app\seed.py, backend\app\scripts\db_seed.py, backend\scripts\db_seed.py, scripts\db_seed.py

### Worker / Scheduler

- Worker related files: None found

## Authentication & RBAC

- Login routes: /login
- Dashboard routes: Unknown
- JWT & CORS support inferred from backend imports.

## Feature Cards

### Feature Group: /

**UI Usage**
- Navigate to `/` → Steps Unknown (needs source)
- Navigate to `/login` → Steps Unknown (needs source)
- Navigate to `/posts/:postId` → Steps Unknown (needs source)
**API Usage**
- POST /compliance-failure (file: backend\app\alerts\test_routes.py)
```bash
curl -X POST http://<HOST:PORT>/compliance-failure -H 'Authorization: Bearer <JWT>'
```
- POST /compliance-failure (file: backend\app\alerts\test_routes.py)
```bash
curl -X POST http://<HOST:PORT>/compliance-failure -H 'Authorization: Bearer <JWT>'
```
- POST /enroll (file: backend\app\routes\agents.py)
```bash
curl -X POST http://<HOST:PORT>/enroll -H 'Authorization: Bearer <JWT>'
```
- GET /config/{agent_id} (file: backend\app\routes\agents.py)
```bash
curl -X GET http://<HOST:PORT>/config/{agent_id} -H 'Authorization: Bearer <JWT>'
```
- POST /enroll (file: backend\app\routes\agents.py)
```bash
curl -X POST http://<HOST:PORT>/enroll -H 'Authorization: Bearer <JWT>'
```
- GET /config/{agent_id} (file: backend\app\routes\agents.py)
```bash
curl -X GET http://<HOST:PORT>/config/{agent_id} -H 'Authorization: Bearer <JWT>'
```
- POST /{agent_id}/logs (file: backend\app\routes\agent_logs.py)
```bash
curl -X POST http://<HOST:PORT>/{agent_id}/logs -H 'Authorization: Bearer <JWT>'
```
- GET /{agent_id}/logs (file: backend\app\routes\agent_logs.py)
```bash
curl -X GET http://<HOST:PORT>/{agent_id}/logs -H 'Authorization: Bearer <JWT>'
```
- POST /{agent_id}/logs (file: backend\app\routes\agent_logs.py)
```bash
curl -X POST http://<HOST:PORT>/{agent_id}/logs -H 'Authorization: Bearer <JWT>'
```
- GET /{agent_id}/logs (file: backend\app\routes\agent_logs.py)
```bash
curl -X GET http://<HOST:PORT>/{agent_id}/logs -H 'Authorization: Bearer <JWT>'
```
- GET / (file: backend\app\routes\alerts.py)
```bash
curl -X GET http://<HOST:PORT>/ -H 'Authorization: Bearer <JWT>'
```
- POST / (file: backend\app\routes\alerts.py)
```bash
curl -X POST http://<HOST:PORT>/ -H 'Authorization: Bearer <JWT>'
```
- PUT /{alert_id} (file: backend\app\routes\alerts.py)
```bash
curl -X PUT http://<HOST:PORT>/{alert_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{alert_id} (file: backend\app\routes\alerts.py)
```bash
curl -X DELETE http://<HOST:PORT>/{alert_id} -H 'Authorization: Bearer <JWT>'
```
- GET / (file: backend\app\routes\alerts.py)
```bash
curl -X GET http://<HOST:PORT>/ -H 'Authorization: Bearer <JWT>'
```
- POST / (file: backend\app\routes\alerts.py)
```bash
curl -X POST http://<HOST:PORT>/ -H 'Authorization: Bearer <JWT>'
```
- PUT /{alert_id} (file: backend\app\routes\alerts.py)
```bash
curl -X PUT http://<HOST:PORT>/{alert_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{alert_id} (file: backend\app\routes\alerts.py)
```bash
curl -X DELETE http://<HOST:PORT>/{alert_id} -H 'Authorization: Bearer <JWT>'
```
- POST /auth/login (file: backend\app\routes\auth.py)
```bash
curl -X POST http://<HOST:PORT>/auth/login -H 'Authorization: Bearer <JWT>'
```
- GET /auth/me (file: backend\app\routes\auth.py)
```bash
curl -X GET http://<HOST:PORT>/auth/me -H 'Authorization: Bearer <JWT>'
```
- POST /auth/login (file: backend\app\routes\auth.py)
```bash
curl -X POST http://<HOST:PORT>/auth/login -H 'Authorization: Bearer <JWT>'
```
- GET /auth/me (file: backend\app\routes\auth.py)
```bash
curl -X GET http://<HOST:PORT>/auth/me -H 'Authorization: Bearer <JWT>'
```
- GET /trends (file: backend\app\routes\compliance.py)
```bash
curl -X GET http://<HOST:PORT>/trends -H 'Authorization: Bearer <JWT>'
```
- GET /trends (file: backend\app\routes\compliance.py)
```bash
curl -X GET http://<HOST:PORT>/trends -H 'Authorization: Bearer <JWT>'
```
- GET /export.csv (file: backend\app\routes\compliance_export.py)
```bash
curl -X GET http://<HOST:PORT>/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /export.pdf (file: backend\app\routes\compliance_export.py)
```bash
curl -X GET http://<HOST:PORT>/export.pdf -H 'Authorization: Bearer <JWT>'
```
- GET /export.csv (file: backend\app\routes\compliance_export.py)
```bash
curl -X GET http://<HOST:PORT>/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /export.pdf (file: backend\app\routes\compliance_export.py)
```bash
curl -X GET http://<HOST:PORT>/export.pdf -H 'Authorization: Bearer <JWT>'
```
- PATCH /{origin_id} (file: backend\app\routes\cors_admin.py)
```bash
curl -X PATCH http://<HOST:PORT>/{origin_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{origin_id} (file: backend\app\routes\cors_admin.py)
```bash
curl -X DELETE http://<HOST:PORT>/{origin_id} -H 'Authorization: Bearer <JWT>'
```
- PATCH /{origin_id} (file: backend\app\routes\cors_admin.py)
```bash
curl -X PATCH http://<HOST:PORT>/{origin_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{origin_id} (file: backend\app\routes\cors_admin.py)
```bash
curl -X DELETE http://<HOST:PORT>/{origin_id} -H 'Authorization: Bearer <JWT>'
```
- GET /zip (file: backend\app\routes\export.py)
```bash
curl -X GET http://<HOST:PORT>/zip -H 'Authorization: Bearer <JWT>'
```
- GET /zip (file: backend\app\routes\export.py)
```bash
curl -X GET http://<HOST:PORT>/zip -H 'Authorization: Bearer <JWT>'
```
- GET /health (file: backend\app\routes\health.py)
```bash
curl -X GET http://<HOST:PORT>/health -H 'Authorization: Bearer <JWT>'
```
- GET /health (file: backend\app\routes\health.py)
```bash
curl -X GET http://<HOST:PORT>/health -H 'Authorization: Bearer <JWT>'
```
- GET /healthz (file: backend\app\routes\healthz.py)
```bash
curl -X GET http://<HOST:PORT>/healthz -H 'Authorization: Bearer <JWT>'
```
- GET /healthz (file: backend\app\routes\healthz.py)
```bash
curl -X GET http://<HOST:PORT>/healthz -H 'Authorization: Bearer <JWT>'
```
- GET /logs (file: backend\app\routes\logs.py)
```bash
curl -X GET http://<HOST:PORT>/logs -H 'Authorization: Bearer <JWT>'
```
- GET /logs (file: backend\app\routes\logs.py)
```bash
curl -X GET http://<HOST:PORT>/logs -H 'Authorization: Bearer <JWT>'
```
- GET /metrics (file: backend\app\routes\metrics.py)
```bash
curl -X GET http://<HOST:PORT>/metrics -H 'Authorization: Bearer <JWT>'
```
- GET /metrics (file: backend\app\routes\metrics.py)
```bash
curl -X GET http://<HOST:PORT>/metrics -H 'Authorization: Bearer <JWT>'
```
- GET / (file: backend\app\routes\modules.py)
```bash
curl -X GET http://<HOST:PORT>/ -H 'Authorization: Bearer <JWT>'
```
- PUT /{module_id} (file: backend\app\routes\modules.py)
```bash
curl -X PUT http://<HOST:PORT>/{module_id} -H 'Authorization: Bearer <JWT>'
```
- POST / (file: backend\app\routes\modules.py)
```bash
curl -X POST http://<HOST:PORT>/ -H 'Authorization: Bearer <JWT>'
```
- GET / (file: backend\app\routes\modules.py)
```bash
curl -X GET http://<HOST:PORT>/ -H 'Authorization: Bearer <JWT>'
```
- PUT /{module_id} (file: backend\app\routes\modules.py)
```bash
curl -X PUT http://<HOST:PORT>/{module_id} -H 'Authorization: Bearer <JWT>'
```
- POST / (file: backend\app\routes\modules.py)
```bash
curl -X POST http://<HOST:PORT>/ -H 'Authorization: Bearer <JWT>'
```
- GET /mapping (file: backend\app\routes\module_mapping.py)
```bash
curl -X GET http://<HOST:PORT>/mapping -H 'Authorization: Bearer <JWT>'
```
- PUT /mapping (file: backend\app\routes\module_mapping.py)
```bash
curl -X PUT http://<HOST:PORT>/mapping -H 'Authorization: Bearer <JWT>'
```
- GET /mapping (file: backend\app\routes\module_mapping.py)
```bash
curl -X GET http://<HOST:PORT>/mapping -H 'Authorization: Bearer <JWT>'
```
- PUT /mapping (file: backend\app\routes\module_mapping.py)
```bash
curl -X PUT http://<HOST:PORT>/mapping -H 'Authorization: Bearer <JWT>'
```
- POST /send/{notification_id} (file: backend\app\routes\notifications.py)
```bash
curl -X POST http://<HOST:PORT>/send/{notification_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{notification_id} (file: backend\app\routes\notifications.py)
```bash
curl -X DELETE http://<HOST:PORT>/{notification_id} -H 'Authorization: Bearer <JWT>'
```
- POST /send/{notification_id} (file: backend\app\routes\notifications.py)
```bash
curl -X POST http://<HOST:PORT>/send/{notification_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{notification_id} (file: backend\app\routes\notifications.py)
```bash
curl -X DELETE http://<HOST:PORT>/{notification_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{role_id} (file: backend\app\routes\roles.py)
```bash
curl -X DELETE http://<HOST:PORT>/{role_id} -H 'Authorization: Bearer <JWT>'
```
- POST /assign (file: backend\app\routes\roles.py)
```bash
curl -X POST http://<HOST:PORT>/assign -H 'Authorization: Bearer <JWT>'
```
- DELETE /{role_id} (file: backend\app\routes\roles.py)
```bash
curl -X DELETE http://<HOST:PORT>/{role_id} -H 'Authorization: Bearer <JWT>'
```
- POST /assign (file: backend\app\routes\roles.py)
```bash
curl -X POST http://<HOST:PORT>/assign -H 'Authorization: Bearer <JWT>'
```
- GET /files (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/files -H 'Authorization: Bearer <JWT>'
```
- GET /network (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/network -H 'Authorization: Bearer <JWT>'
```
- GET /files/export.csv (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/files/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /network/export.csv (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/network/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /files (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/files -H 'Authorization: Bearer <JWT>'
```
- GET /network (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/network -H 'Authorization: Bearer <JWT>'
```
- GET /files/export.csv (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/files/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /network/export.csv (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/network/export.csv -H 'Authorization: Bearer <JWT>'
```
- PUT /me (file: backend\app\routes\users.py)
```bash
curl -X PUT http://<HOST:PORT>/me -H 'Authorization: Bearer <JWT>'
```
- PUT /me (file: backend\app\routes\users.py)
```bash
curl -X PUT http://<HOST:PORT>/me -H 'Authorization: Bearer <JWT>'
```
- GET /users (file: backend\app\routes\users_admin.py)
```bash
curl -X GET http://<HOST:PORT>/users -H 'Authorization: Bearer <JWT>'
```
- POST /users (file: backend\app\routes\users_admin.py)
```bash
curl -X POST http://<HOST:PORT>/users -H 'Authorization: Bearer <JWT>'
```
- GET /users (file: backend\app\routes\users_admin.py)
```bash
curl -X GET http://<HOST:PORT>/users -H 'Authorization: Bearer <JWT>'
```
- POST /users (file: backend\app\routes\users_admin.py)
```bash
curl -X POST http://<HOST:PORT>/users -H 'Authorization: Bearer <JWT>'
```
- GET /users/me (file: backend\app\routes\users_me.py)
```bash
curl -X GET http://<HOST:PORT>/users/me -H 'Authorization: Bearer <JWT>'
```
- PUT /users/me (file: backend\app\routes\users_me.py)
```bash
curl -X PUT http://<HOST:PORT>/users/me -H 'Authorization: Bearer <JWT>'
```
- GET /users/me (file: backend\app\routes\users_me.py)
```bash
curl -X GET http://<HOST:PORT>/users/me -H 'Authorization: Bearer <JWT>'
```
- PUT /users/me (file: backend\app\routes\users_me.py)
```bash
curl -X PUT http://<HOST:PORT>/users/me -H 'Authorization: Bearer <JWT>'
```
- GET /files (file: backend\app\routes\visibility.py)
```bash
curl -X GET http://<HOST:PORT>/files -H 'Authorization: Bearer <JWT>'
```
- GET /network (file: backend\app\routes\visibility.py)
```bash
curl -X GET http://<HOST:PORT>/network -H 'Authorization: Bearer <JWT>'
```
- GET /files (file: backend\app\routes\visibility.py)
```bash
curl -X GET http://<HOST:PORT>/files -H 'Authorization: Bearer <JWT>'
```
- GET /network (file: backend\app\routes\visibility.py)
```bash
curl -X GET http://<HOST:PORT>/network -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /assign

**UI Usage**
- No UI routes found.
**API Usage**
- POST /assign (file: backend\app\routes\roles.py)
```bash
curl -X POST http://<HOST:PORT>/assign -H 'Authorization: Bearer <JWT>'
```
- POST /assign (file: backend\app\routes\roles.py)
```bash
curl -X POST http://<HOST:PORT>/assign -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /auth

**UI Usage**
- No UI routes found.
**API Usage**
- POST /auth/login (file: backend\app\routes\auth.py)
```bash
curl -X POST http://<HOST:PORT>/auth/login -H 'Authorization: Bearer <JWT>'
```
- GET /auth/me (file: backend\app\routes\auth.py)
```bash
curl -X GET http://<HOST:PORT>/auth/me -H 'Authorization: Bearer <JWT>'
```
- POST /auth/login (file: backend\app\routes\auth.py)
```bash
curl -X POST http://<HOST:PORT>/auth/login -H 'Authorization: Bearer <JWT>'
```
- GET /auth/me (file: backend\app\routes\auth.py)
```bash
curl -X GET http://<HOST:PORT>/auth/me -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /compliance-failure

**UI Usage**
- No UI routes found.
**API Usage**
- POST /compliance-failure (file: backend\app\alerts\test_routes.py)
```bash
curl -X POST http://<HOST:PORT>/compliance-failure -H 'Authorization: Bearer <JWT>'
```
- POST /compliance-failure (file: backend\app\alerts\test_routes.py)
```bash
curl -X POST http://<HOST:PORT>/compliance-failure -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /config

**UI Usage**
- No UI routes found.
**API Usage**
- GET /config/{agent_id} (file: backend\app\routes\agents.py)
```bash
curl -X GET http://<HOST:PORT>/config/{agent_id} -H 'Authorization: Bearer <JWT>'
```
- GET /config/{agent_id} (file: backend\app\routes\agents.py)
```bash
curl -X GET http://<HOST:PORT>/config/{agent_id} -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /enroll

**UI Usage**
- No UI routes found.
**API Usage**
- POST /enroll (file: backend\app\routes\agents.py)
```bash
curl -X POST http://<HOST:PORT>/enroll -H 'Authorization: Bearer <JWT>'
```
- POST /enroll (file: backend\app\routes\agents.py)
```bash
curl -X POST http://<HOST:PORT>/enroll -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /export.csv

**UI Usage**
- No UI routes found.
**API Usage**
- GET /export.csv (file: backend\app\routes\compliance_export.py)
```bash
curl -X GET http://<HOST:PORT>/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /export.csv (file: backend\app\routes\compliance_export.py)
```bash
curl -X GET http://<HOST:PORT>/export.csv -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /export.pdf

**UI Usage**
- No UI routes found.
**API Usage**
- GET /export.pdf (file: backend\app\routes\compliance_export.py)
```bash
curl -X GET http://<HOST:PORT>/export.pdf -H 'Authorization: Bearer <JWT>'
```
- GET /export.pdf (file: backend\app\routes\compliance_export.py)
```bash
curl -X GET http://<HOST:PORT>/export.pdf -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /files

**UI Usage**
- No UI routes found.
**API Usage**
- GET /files (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/files -H 'Authorization: Bearer <JWT>'
```
- GET /files/export.csv (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/files/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /files (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/files -H 'Authorization: Bearer <JWT>'
```
- GET /files/export.csv (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/files/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /files (file: backend\app\routes\visibility.py)
```bash
curl -X GET http://<HOST:PORT>/files -H 'Authorization: Bearer <JWT>'
```
- GET /files (file: backend\app\routes\visibility.py)
```bash
curl -X GET http://<HOST:PORT>/files -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /health

**UI Usage**
- No UI routes found.
**API Usage**
- GET /health (file: backend\app\routes\health.py)
```bash
curl -X GET http://<HOST:PORT>/health -H 'Authorization: Bearer <JWT>'
```
- GET /health (file: backend\app\routes\health.py)
```bash
curl -X GET http://<HOST:PORT>/health -H 'Authorization: Bearer <JWT>'
```
- GET /healthz (file: backend\app\routes\healthz.py)
```bash
curl -X GET http://<HOST:PORT>/healthz -H 'Authorization: Bearer <JWT>'
```
- GET /healthz (file: backend\app\routes\healthz.py)
```bash
curl -X GET http://<HOST:PORT>/healthz -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /healthz

**UI Usage**
- No UI routes found.
**API Usage**
- GET /healthz (file: backend\app\routes\healthz.py)
```bash
curl -X GET http://<HOST:PORT>/healthz -H 'Authorization: Bearer <JWT>'
```
- GET /healthz (file: backend\app\routes\healthz.py)
```bash
curl -X GET http://<HOST:PORT>/healthz -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /logs

**UI Usage**
- No UI routes found.
**API Usage**
- GET /logs (file: backend\app\routes\logs.py)
```bash
curl -X GET http://<HOST:PORT>/logs -H 'Authorization: Bearer <JWT>'
```
- GET /logs (file: backend\app\routes\logs.py)
```bash
curl -X GET http://<HOST:PORT>/logs -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /mapping

**UI Usage**
- No UI routes found.
**API Usage**
- GET /mapping (file: backend\app\routes\module_mapping.py)
```bash
curl -X GET http://<HOST:PORT>/mapping -H 'Authorization: Bearer <JWT>'
```
- PUT /mapping (file: backend\app\routes\module_mapping.py)
```bash
curl -X PUT http://<HOST:PORT>/mapping -H 'Authorization: Bearer <JWT>'
```
- GET /mapping (file: backend\app\routes\module_mapping.py)
```bash
curl -X GET http://<HOST:PORT>/mapping -H 'Authorization: Bearer <JWT>'
```
- PUT /mapping (file: backend\app\routes\module_mapping.py)
```bash
curl -X PUT http://<HOST:PORT>/mapping -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /me

**UI Usage**
- No UI routes found.
**API Usage**
- GET /metrics (file: backend\app\routes\metrics.py)
```bash
curl -X GET http://<HOST:PORT>/metrics -H 'Authorization: Bearer <JWT>'
```
- GET /metrics (file: backend\app\routes\metrics.py)
```bash
curl -X GET http://<HOST:PORT>/metrics -H 'Authorization: Bearer <JWT>'
```
- PUT /me (file: backend\app\routes\users.py)
```bash
curl -X PUT http://<HOST:PORT>/me -H 'Authorization: Bearer <JWT>'
```
- PUT /me (file: backend\app\routes\users.py)
```bash
curl -X PUT http://<HOST:PORT>/me -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /metrics

**UI Usage**
- No UI routes found.
**API Usage**
- GET /metrics (file: backend\app\routes\metrics.py)
```bash
curl -X GET http://<HOST:PORT>/metrics -H 'Authorization: Bearer <JWT>'
```
- GET /metrics (file: backend\app\routes\metrics.py)
```bash
curl -X GET http://<HOST:PORT>/metrics -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /network

**UI Usage**
- No UI routes found.
**API Usage**
- GET /network (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/network -H 'Authorization: Bearer <JWT>'
```
- GET /network/export.csv (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/network/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /network (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/network -H 'Authorization: Bearer <JWT>'
```
- GET /network/export.csv (file: backend\app\routes\scan_results.py)
```bash
curl -X GET http://<HOST:PORT>/network/export.csv -H 'Authorization: Bearer <JWT>'
```
- GET /network (file: backend\app\routes\visibility.py)
```bash
curl -X GET http://<HOST:PORT>/network -H 'Authorization: Bearer <JWT>'
```
- GET /network (file: backend\app\routes\visibility.py)
```bash
curl -X GET http://<HOST:PORT>/network -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /send

**UI Usage**
- No UI routes found.
**API Usage**
- POST /send/{notification_id} (file: backend\app\routes\notifications.py)
```bash
curl -X POST http://<HOST:PORT>/send/{notification_id} -H 'Authorization: Bearer <JWT>'
```
- POST /send/{notification_id} (file: backend\app\routes\notifications.py)
```bash
curl -X POST http://<HOST:PORT>/send/{notification_id} -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /trends

**UI Usage**
- No UI routes found.
**API Usage**
- GET /trends (file: backend\app\routes\compliance.py)
```bash
curl -X GET http://<HOST:PORT>/trends -H 'Authorization: Bearer <JWT>'
```
- GET /trends (file: backend\app\routes\compliance.py)
```bash
curl -X GET http://<HOST:PORT>/trends -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /users

**UI Usage**
- No UI routes found.
**API Usage**
- GET /users (file: backend\app\routes\users_admin.py)
```bash
curl -X GET http://<HOST:PORT>/users -H 'Authorization: Bearer <JWT>'
```
- POST /users (file: backend\app\routes\users_admin.py)
```bash
curl -X POST http://<HOST:PORT>/users -H 'Authorization: Bearer <JWT>'
```
- GET /users (file: backend\app\routes\users_admin.py)
```bash
curl -X GET http://<HOST:PORT>/users -H 'Authorization: Bearer <JWT>'
```
- POST /users (file: backend\app\routes\users_admin.py)
```bash
curl -X POST http://<HOST:PORT>/users -H 'Authorization: Bearer <JWT>'
```
- GET /users/me (file: backend\app\routes\users_me.py)
```bash
curl -X GET http://<HOST:PORT>/users/me -H 'Authorization: Bearer <JWT>'
```
- PUT /users/me (file: backend\app\routes\users_me.py)
```bash
curl -X PUT http://<HOST:PORT>/users/me -H 'Authorization: Bearer <JWT>'
```
- GET /users/me (file: backend\app\routes\users_me.py)
```bash
curl -X GET http://<HOST:PORT>/users/me -H 'Authorization: Bearer <JWT>'
```
- PUT /users/me (file: backend\app\routes\users_me.py)
```bash
curl -X PUT http://<HOST:PORT>/users/me -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /zip

**UI Usage**
- No UI routes found.
**API Usage**
- GET /zip (file: backend\app\routes\export.py)
```bash
curl -X GET http://<HOST:PORT>/zip -H 'Authorization: Bearer <JWT>'
```
- GET /zip (file: backend\app\routes\export.py)
```bash
curl -X GET http://<HOST:PORT>/zip -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /{agent_id}

**UI Usage**
- No UI routes found.
**API Usage**
- POST /{agent_id}/logs (file: backend\app\routes\agent_logs.py)
```bash
curl -X POST http://<HOST:PORT>/{agent_id}/logs -H 'Authorization: Bearer <JWT>'
```
- GET /{agent_id}/logs (file: backend\app\routes\agent_logs.py)
```bash
curl -X GET http://<HOST:PORT>/{agent_id}/logs -H 'Authorization: Bearer <JWT>'
```
- POST /{agent_id}/logs (file: backend\app\routes\agent_logs.py)
```bash
curl -X POST http://<HOST:PORT>/{agent_id}/logs -H 'Authorization: Bearer <JWT>'
```
- GET /{agent_id}/logs (file: backend\app\routes\agent_logs.py)
```bash
curl -X GET http://<HOST:PORT>/{agent_id}/logs -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /{alert_id}

**UI Usage**
- No UI routes found.
**API Usage**
- PUT /{alert_id} (file: backend\app\routes\alerts.py)
```bash
curl -X PUT http://<HOST:PORT>/{alert_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{alert_id} (file: backend\app\routes\alerts.py)
```bash
curl -X DELETE http://<HOST:PORT>/{alert_id} -H 'Authorization: Bearer <JWT>'
```
- PUT /{alert_id} (file: backend\app\routes\alerts.py)
```bash
curl -X PUT http://<HOST:PORT>/{alert_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{alert_id} (file: backend\app\routes\alerts.py)
```bash
curl -X DELETE http://<HOST:PORT>/{alert_id} -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /{module_id}

**UI Usage**
- No UI routes found.
**API Usage**
- PUT /{module_id} (file: backend\app\routes\modules.py)
```bash
curl -X PUT http://<HOST:PORT>/{module_id} -H 'Authorization: Bearer <JWT>'
```
- PUT /{module_id} (file: backend\app\routes\modules.py)
```bash
curl -X PUT http://<HOST:PORT>/{module_id} -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /{notification_id}

**UI Usage**
- No UI routes found.
**API Usage**
- DELETE /{notification_id} (file: backend\app\routes\notifications.py)
```bash
curl -X DELETE http://<HOST:PORT>/{notification_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{notification_id} (file: backend\app\routes\notifications.py)
```bash
curl -X DELETE http://<HOST:PORT>/{notification_id} -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /{origin_id}

**UI Usage**
- No UI routes found.
**API Usage**
- PATCH /{origin_id} (file: backend\app\routes\cors_admin.py)
```bash
curl -X PATCH http://<HOST:PORT>/{origin_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{origin_id} (file: backend\app\routes\cors_admin.py)
```bash
curl -X DELETE http://<HOST:PORT>/{origin_id} -H 'Authorization: Bearer <JWT>'
```
- PATCH /{origin_id} (file: backend\app\routes\cors_admin.py)
```bash
curl -X PATCH http://<HOST:PORT>/{origin_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{origin_id} (file: backend\app\routes\cors_admin.py)
```bash
curl -X DELETE http://<HOST:PORT>/{origin_id} -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

### Feature Group: /{role_id}

**UI Usage**
- No UI routes found.
**API Usage**
- DELETE /{role_id} (file: backend\app\routes\roles.py)
```bash
curl -X DELETE http://<HOST:PORT>/{role_id} -H 'Authorization: Bearer <JWT>'
```
- DELETE /{role_id} (file: backend\app\routes\roles.py)
```bash
curl -X DELETE http://<HOST:PORT>/{role_id} -H 'Authorization: Bearer <JWT>'
```
**Validation Checklist**
- UI loads without errors
- API returns 2xx for valid input
- RBAC enforced if roles are required

## System Health & Observability

- Health endpoints: check `/health`
- Metrics endpoints: check `/metrics` if defined
- Prometheus configs: see docker/observability configs

## Troubleshooting

- **401/403**: JWT or CORS issue
- **404**: Wrong path
- **500**: Backend error, check logs

## Validation Playbook (A1–E22)

- A1: Visiting `/` without token → redirect `/login`
- A2: Valid login → redirect `/dashboard`
- A3: Protected route without token → `/login`
- A4: Logout clears token → `/login`
- ... continue through E22

## Appendices

### API Index

- GET ", summary= (source: backend\app\routes\assets.py)
- GET ", summary= (source: backend\app\routes\assets.py)
- GET ", summary= (source: backend\app\routes\schedules.py)
- GET ", summary= (source: backend\app\routes\schedules.py)
- GET / (source: backend\app\routes\alerts.py)
- GET / (source: backend\app\routes\alerts.py)
- GET / (source: backend\app\routes\modules.py)
- GET / (source: backend\app\routes\modules.py)
- POST / (source: backend\app\routes\alerts.py)
- POST / (source: backend\app\routes\alerts.py)
- POST / (source: backend\app\routes\modules.py)
- POST / (source: backend\app\routes\modules.py)
- POST /assign (source: backend\app\routes\roles.py)
- POST /assign (source: backend\app\routes\roles.py)
- POST /auth/login (source: backend\app\routes\auth.py)
- POST /auth/login (source: backend\app\routes\auth.py)
- GET /auth/me (source: backend\app\routes\auth.py)
- GET /auth/me (source: backend\app\routes\auth.py)
- POST /compliance-failure (source: backend\app\alerts\test_routes.py)
- POST /compliance-failure (source: backend\app\alerts\test_routes.py)
- GET /config/{agent_id} (source: backend\app\routes\agents.py)
- GET /config/{agent_id} (source: backend\app\routes\agents.py)
- POST /enroll (source: backend\app\routes\agents.py)
- POST /enroll (source: backend\app\routes\agents.py)
- GET /export.csv (source: backend\app\routes\compliance_export.py)
- GET /export.csv (source: backend\app\routes\compliance_export.py)
- GET /export.pdf (source: backend\app\routes\compliance_export.py)
- GET /export.pdf (source: backend\app\routes\compliance_export.py)
- GET /files (source: backend\app\routes\scan_results.py)
- GET /files (source: backend\app\routes\scan_results.py)
- GET /files (source: backend\app\routes\visibility.py)
- GET /files (source: backend\app\routes\visibility.py)
- GET /files/export.csv (source: backend\app\routes\scan_results.py)
- GET /files/export.csv (source: backend\app\routes\scan_results.py)
- GET /health (source: backend\app\routes\health.py)
- GET /health (source: backend\app\routes\health.py)
- GET /healthz (source: backend\app\routes\healthz.py)
- GET /healthz (source: backend\app\routes\healthz.py)
- GET /logs (source: backend\app\routes\logs.py)
- GET /logs (source: backend\app\routes\logs.py)
- GET /mapping (source: backend\app\routes\module_mapping.py)
- GET /mapping (source: backend\app\routes\module_mapping.py)
- PUT /mapping (source: backend\app\routes\module_mapping.py)
- PUT /mapping (source: backend\app\routes\module_mapping.py)
- PUT /me (source: backend\app\routes\users.py)
- PUT /me (source: backend\app\routes\users.py)
- GET /metrics (source: backend\app\routes\metrics.py)
- GET /metrics (source: backend\app\routes\metrics.py)
- GET /network (source: backend\app\routes\scan_results.py)
- GET /network (source: backend\app\routes\scan_results.py)
- GET /network (source: backend\app\routes\visibility.py)
- GET /network (source: backend\app\routes\visibility.py)
- GET /network/export.csv (source: backend\app\routes\scan_results.py)
- GET /network/export.csv (source: backend\app\routes\scan_results.py)
- POST /send/{notification_id} (source: backend\app\routes\notifications.py)
- POST /send/{notification_id} (source: backend\app\routes\notifications.py)
- GET /trends (source: backend\app\routes\compliance.py)
- GET /trends (source: backend\app\routes\compliance.py)
- GET /users (source: backend\app\routes\users_admin.py)
- GET /users (source: backend\app\routes\users_admin.py)
- POST /users (source: backend\app\routes\users_admin.py)
- POST /users (source: backend\app\routes\users_admin.py)
- GET /users/me (source: backend\app\routes\users_me.py)
- GET /users/me (source: backend\app\routes\users_me.py)
- PUT /users/me (source: backend\app\routes\users_me.py)
- PUT /users/me (source: backend\app\routes\users_me.py)
- GET /zip (source: backend\app\routes\export.py)
- GET /zip (source: backend\app\routes\export.py)
- GET /{agent_id}/logs (source: backend\app\routes\agent_logs.py)
- GET /{agent_id}/logs (source: backend\app\routes\agent_logs.py)
- POST /{agent_id}/logs (source: backend\app\routes\agent_logs.py)
- POST /{agent_id}/logs (source: backend\app\routes\agent_logs.py)
- DELETE /{alert_id} (source: backend\app\routes\alerts.py)
- DELETE /{alert_id} (source: backend\app\routes\alerts.py)
- PUT /{alert_id} (source: backend\app\routes\alerts.py)
- PUT /{alert_id} (source: backend\app\routes\alerts.py)
- PUT /{module_id} (source: backend\app\routes\modules.py)
- PUT /{module_id} (source: backend\app\routes\modules.py)
- DELETE /{notification_id} (source: backend\app\routes\notifications.py)
- DELETE /{notification_id} (source: backend\app\routes\notifications.py)
- DELETE /{origin_id} (source: backend\app\routes\cors_admin.py)
- DELETE /{origin_id} (source: backend\app\routes\cors_admin.py)
- PATCH /{origin_id} (source: backend\app\routes\cors_admin.py)
- PATCH /{origin_id} (source: backend\app\routes\cors_admin.py)
- DELETE /{role_id} (source: backend\app\routes\roles.py)
- DELETE /{role_id} (source: backend\app\routes\roles.py)
### UI Routes

- / (file: frontend\src\App.jsx)
- /login (file: frontend\src\App.jsx)
- /posts/:postId (file: node_modules\react-router\dist\development\index.d.ts)
- /posts/:postId (file: node_modules\react-router\dist\production\index.d.ts)