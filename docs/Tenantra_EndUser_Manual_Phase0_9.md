# Tenantra End‑User Manual — Phases 0→9 (Derived from ZIP)

**Scope:** This manual is auto‑generated from the provided repository snapshot. No assumptions were made beyond code evidence. Unknowns are marked **Unknown (needs source)**.

## 1. Global Prerequisites
- **Detected env keys (from code):** ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_PASS, ADMIN_USER, APP_VERSION, BACKEND_LOG_PATH, BACKEND_URL, BASE_URL, CORS_ALLOWED_HEADERS, CORS_ALLOWED_METHODS, CORS_ALLOWED_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_DB_CACHE_TTL, CORS_MAX_AGE, DATABASE_URL, DB_HOST, DB_PORT, DB_URL, FRONTEND_PATH, FRONTEND_URL, JWT_ALGORITHM, JWT_SECRET, JWT_SECRET_KEY, LOG_DIR, LOG_FORMAT, LOG_LEVEL, OBS_SQL_PROFILER, POSTGRES_DATABASE, POSTGRES_DB, POSTGRES_DBNAME, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER, RATE_LIMIT_DEFAULT, RATE_LIMIT_OVERRIDES, RATE_LIMIT_WINDOW, REFRESH_IN_COOKIE, REFRESH_TOKEN_EXPIRE_DAYS, SEC_COEP, SEC_CONTENT_TYPE_OPTIONS, SEC_COOP, SEC_CSP, SEC_FORCE_HSTS, SEC_FRAME_OPTIONS, SEC_HSTS, SEC_REFERRER_POLICY, SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD, SEED_ADMIN_ROLE, SEED_ADMIN_TENANT_ID, SEED_ADMIN_USERNAME, SEED_TENANT_NAME, SEED_TENANT_SLUG, SLOW_SQL_MS, SMTP_FROM, SMTP_HOST, SMTP_PASS, SMTP_PORT, SMTP_TLS, SMTP_USER, TENANTRA_DEV_CORS_DEFAULT, TENANTRA_ENABLE_NOTIFICATIONS_WORKER, TENANTRA_ENC_KEY, TENANTRA_EXPORT_RATE_MAX, TENANTRA_EXPORT_RATE_WINDOW_SECONDS, TENANTRA_METRIC_LATENCY_BUCKETS, TENANT_NAME
- **JWT usage hints:** backend\app\core\auth.py, backend\app\core\secrets.py, backend\app\core\security.py, backend\app\dependencies\auth.py, backend\app\main.py, backend\app\routes\auth.py, backend\app\routes\users_admin.py, backend\app\routes\users_me.py, backend\tests\test_export_audit_router.py, backend\tests\test_user_profile.py
- **CORS config hints:** backend\alembic\versions\_archive\c41a5d2e7f10_s14_refresh_tokens_table.py, backend\alembic\versions\_archive\d6e4f1a2b3c4_s15_tenant_cors_origins.py, backend\app\main.py, backend\app\middleware\dynamic_cors.py, backend\app\models\tenant_cors_origin.py, backend\app\routes\cors_admin.py, tools\phase8_deep_audit.py, tools\validate_tenantra_phases.py
- **RBAC hints:** backend\alembic\versions\T_000_unified_base.py, backend\alembic\versions\_archive\0003_add_role_column_to_users.py, backend\alembic\versions\_archive\0004_create_roles.py, backend\alembic\versions\_archive\0005_create_audit_log.py, backend\alembic\versions\_archive\0006_add_timestamps_log.py, backend\alembic\versions\_archive\0006_add_timestamps_to_roles_and_audit_log.py, backend\alembic\versions\_archive\7f9a2c1e6b01_s7_db_integrity_indexes.py, backend\app\core\auth.py, backend\app\core\permissions.py, backend\app\core\rbac.py, backend\app\dependencies\auth.py, backend\app\main.py, backend\app\models\__init__.py, backend\app\models\role.py, backend\app\models\user.py, backend\app\routes\agents.py, backend\app\routes\assets.py, backend\app\routes\audit_logs.py, backend\app\routes\auth.py, backend\app\routes\compliance.py, backend\app\routes\cors_admin.py, backend\app\routes\export.py, backend\app\routes\logs.py, backend\app\routes\modules.py, backend\app\routes\notifications.py, backend\app\routes\roles.py, backend\app\routes\schedules.py, backend\app\routes\users.py, backend\app\routes\users_admin.py, backend\app\routes\users_me.py, backend\app\routes\visibility.py, backend\app\schemas\user_schema.py, backend\app\scripts\db_seed.py, backend\app\scripts\promote_admin.py, backend\app\utils\rbac.py, backend\promote_admin.py, backend\scripts\db_check.py, backend\scripts\db_sanity.py, backend\scripts\db_seed.py, backend\tests\test_export_audit_router.py, promote_admin.py, tests\test_access_control.py, tools\phase8_deep_audit.py, tools\validate_tenantra_phases.py
- **Alembic migrations:** 0 files
- **Seed scripts:** backend\app\seed.py, backend\app\scripts\db_seed.py, backend\scripts\db_seed.py, scripts\db_seed.py
- **Worker/Scheduler hints:** None found

## 2. UI Feature Map (by Route Prefix)
### /
- **Routes:** /
- **Menu links (if any):**
  - /
  - /SpOnGe-bOB
  - /alerts
  - /compliance
  - /compliance-trends
  - /dashboard
  - /login
  - /logout
  - /logs
  - /message
  - /messages
  - /notifications
  - /profile
  - /some/path
  - /somewhere/else
  - /tasks
  - /users
### /about
- **Routes:** /about/contact-us
- **Menu links (if any):**
  - None detected
### /account
- **Routes:** /account
- **Menu links (if any):**
  - None detected
### /blog
- **Routes:** /blog
- **Menu links (if any):**
  - None detected
### /dashboard
- **Routes:** /dashboard
- **Menu links (if any):**
  - /dashboard
### /login
- **Routes:** /login
- **Menu links (if any):**
  - /login
### /parent
- **Routes:** /parent
- **Menu links (if any):**
  - None detected
### /posts
- **Routes:** /posts/:postId
- **Menu links (if any):**
  - None detected
### /root-sibling
- **Routes:** /root-sibling
- **Menu links (if any):**
  - None detected

## 3. API Surface (from decorators/OpenAPI)
### 3.1 From backend decorators
#### Group: /
- `GET /`  _(source: backend\app\routes\alerts.py)_
- `GET /`  _(source: backend\app\routes\modules.py)_
- `GET /`  _(source: backend\app\routes\alerts.py)_
- `GET /`  _(source: backend\app\routes\modules.py)_
#### Group: ")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description=
- `GET ")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description=`  _(source: backend\app\routes\audit_logs.py)_
- `GET ")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description=`  _(source: backend\app\routes\audit_logs.py)_
#### Group: ", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    rows = db.query(Notification).order_by(Notification.id.desc()).all()
    return rows

@router.post(
- `GET ", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    rows = db.query(Notification).order_by(Notification.id.desc()).all()
    return rows

@router.post(`  _(source: backend\app\routes\notifications.py)_
- `GET ", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    rows = db.query(Notification).order_by(Notification.id.desc()).all()
    return rows

@router.post(`  _(source: backend\app\routes\notifications.py)_
#### Group: ", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post(
- `GET ", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post(`  _(source: backend\app\routes\cors_admin.py)_
- `GET ", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post(`  _(source: backend\app\routes\cors_admin.py)_
#### Group: ", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post(
- `GET ", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post(`  _(source: backend\app\routes\roles.py)_
- `GET ", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post(`  _(source: backend\app\routes\roles.py)_
#### Group: ", summary=
- `GET ", summary=`  _(source: backend\app\routes\assets.py)_
- `GET ", summary=`  _(source: backend\app\routes\schedules.py)_
- `GET ", summary=`  _(source: backend\app\routes\assets.py)_
- `GET ", summary=`  _(source: backend\app\routes\schedules.py)_
#### Group: auth
- `POST /auth/login`  _(source: backend\app\routes\auth.py)_
- `POST /auth/login`  _(source: backend\app\routes\auth.py)_
#### Group: compliance-failure
- `POST /compliance-failure`  _(source: backend\app\alerts\test_routes.py)_
- `POST /compliance-failure`  _(source: backend\app\alerts\test_routes.py)_
#### Group: enroll
- `POST /enroll`  _(source: backend\app\routes\agents.py)_
- `POST /enroll`  _(source: backend\app\routes\agents.py)_
#### Group: export.csv
- `GET /export.csv`  _(source: backend\app\routes\compliance_export.py)_
- `GET /export.csv`  _(source: backend\app\routes\compliance_export.py)_
#### Group: files
- `GET /files`  _(source: backend\app\routes\scan_results.py)_
- `GET /files`  _(source: backend\app\routes\visibility.py)_
- `GET /files`  _(source: backend\app\routes\scan_results.py)_
- `GET /files`  _(source: backend\app\routes\visibility.py)_
#### Group: health
- `GET /health`  _(source: backend\app\routes\health.py)_
- `GET /health`  _(source: backend\app\routes\health.py)_
#### Group: healthz
- `GET /healthz`  _(source: backend\app\routes\healthz.py)_
- `GET /healthz`  _(source: backend\app\routes\healthz.py)_
#### Group: logs
- `GET /logs`  _(source: backend\app\routes\logs.py)_
- `GET /logs`  _(source: backend\app\routes\logs.py)_
#### Group: mapping
- `GET /mapping`  _(source: backend\app\routes\module_mapping.py)_
- `GET /mapping`  _(source: backend\app\routes\module_mapping.py)_
#### Group: me
- `PUT /me`  _(source: backend\app\routes\users.py)_
- `PUT /me`  _(source: backend\app\routes\users.py)_
#### Group: metrics
- `GET /metrics`  _(source: backend\app\routes\metrics.py)_
- `GET /metrics`  _(source: backend\app\routes\metrics.py)_
#### Group: trends
- `GET /trends`  _(source: backend\app\routes\compliance.py)_
- `GET /trends`  _(source: backend\app\routes\compliance.py)_
#### Group: users
- `GET /users`  _(source: backend\app\routes\users_admin.py)_
- `GET /users`  _(source: backend\app\routes\users_admin.py)_
- `GET /users/me`  _(source: backend\app\routes\users_me.py)_
- `GET /users/me`  _(source: backend\app\routes\users_me.py)_
#### Group: zip
- `GET /zip`  _(source: backend\app\routes\export.py)_
- `GET /zip`  _(source: backend\app\routes\export.py)_
#### Group: {agent_id}
- `POST /{agent_id}/logs`  _(source: backend\app\routes\agent_logs.py)_
- `POST /{agent_id}/logs`  _(source: backend\app\routes\agent_logs.py)_

## 4. Feature Cards (UI ↔ API)
### Feature: /
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/` — Steps and fields: Unknown (needs source)
**How to use (API):**
- `GET /` — Source: backend\app\routes\alerts.py

```bash
curl -i -X GET "http://<HOST:PORT>/" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /` — Source: backend\app\routes\modules.py

```bash
curl -i -X GET "http://<HOST:PORT>/" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /` — Source: backend\app\routes\alerts.py

```bash
curl -i -X GET "http://<HOST:PORT>/" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /` — Source: backend\app\routes\modules.py

```bash
curl -i -X GET "http://<HOST:PORT>/" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description=
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET ")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description=` — Source: backend\app\routes\audit_logs.py

```bash
curl -i -X GET "http://<HOST:PORT>")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description=" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET ")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description=` — Source: backend\app\routes\audit_logs.py

```bash
curl -i -X GET "http://<HOST:PORT>")
def get_audit_logs(
    user_id: Optional[int] = Query(None, description=" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    rows = db.query(Notification).order_by(Notification.id.desc()).all()
    return rows

@router.post(
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET ", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    rows = db.query(Notification).order_by(Notification.id.desc()).all()
    return rows

@router.post(` — Source: backend\app\routes\notifications.py

```bash
curl -i -X GET "http://<HOST:PORT>", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    rows = db.query(Notification).order_by(Notification.id.desc()).all()
    return rows

@router.post(" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET ", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    rows = db.query(Notification).order_by(Notification.id.desc()).all()
    return rows

@router.post(` — Source: backend\app\routes\notifications.py

```bash
curl -i -X GET "http://<HOST:PORT>", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    rows = db.query(Notification).order_by(Notification.id.desc()).all()
    return rows

@router.post(" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post(
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET ", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post(` — Source: backend\app\routes\cors_admin.py

```bash
curl -i -X GET "http://<HOST:PORT>", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post(" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET ", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post(` — Source: backend\app\routes\cors_admin.py

```bash
curl -i -X GET "http://<HOST:PORT>", response_model=List[dict])
def list_origins(
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(TenantCORSOrigin)
    if tenant_id:
        q = q.filter(TenantCORSOrigin.tenant_id == tenant_id)
    rows = q.order_by(TenantCORSOrigin.id.asc()).all()
    return [_serialize(r) for r in rows]

@router.post(" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post(
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET ", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post(` — Source: backend\app\routes\roles.py

```bash
curl -i -X GET "http://<HOST:PORT>", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post(" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET ", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post(` — Source: backend\app\routes\roles.py

```bash
curl -i -X GET "http://<HOST:PORT>", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post(" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /", summary=
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET ", summary=` — Source: backend\app\routes\assets.py

```bash
curl -i -X GET "http://<HOST:PORT>", summary=" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET ", summary=` — Source: backend\app\routes\schedules.py

```bash
curl -i -X GET "http://<HOST:PORT>", summary=" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET ", summary=` — Source: backend\app\routes\assets.py

```bash
curl -i -X GET "http://<HOST:PORT>", summary=" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET ", summary=` — Source: backend\app\routes\schedules.py

```bash
curl -i -X GET "http://<HOST:PORT>", summary=" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /about
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/about/contact-us` — Steps and fields: Unknown (needs source)
**How to use (API):**
- No API endpoints detected for this prefix.
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /account
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/account` — Steps and fields: Unknown (needs source)
**How to use (API):**
- No API endpoints detected for this prefix.
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /auth
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `POST /auth/login` — Source: backend\app\routes\auth.py

```bash
curl -i -X POST "http://<HOST:PORT>/auth/login" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
- `POST /auth/login` — Source: backend\app\routes\auth.py

```bash
curl -i -X POST "http://<HOST:PORT>/auth/login" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /blog
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/blog` — Steps and fields: Unknown (needs source)
**How to use (API):**
- No API endpoints detected for this prefix.
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /compliance-failure
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `POST /compliance-failure` — Source: backend\app\alerts\test_routes.py

```bash
curl -i -X POST "http://<HOST:PORT>/compliance-failure" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
- `POST /compliance-failure` — Source: backend\app\alerts\test_routes.py

```bash
curl -i -X POST "http://<HOST:PORT>/compliance-failure" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /dashboard
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/dashboard` — Steps and fields: Unknown (needs source)
**How to use (API):**
- No API endpoints detected for this prefix.
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /enroll
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `POST /enroll` — Source: backend\app\routes\agents.py

```bash
curl -i -X POST "http://<HOST:PORT>/enroll" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
- `POST /enroll` — Source: backend\app\routes\agents.py

```bash
curl -i -X POST "http://<HOST:PORT>/enroll" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /export.csv
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /export.csv` — Source: backend\app\routes\compliance_export.py

```bash
curl -i -X GET "http://<HOST:PORT>/export.csv" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /export.csv` — Source: backend\app\routes\compliance_export.py

```bash
curl -i -X GET "http://<HOST:PORT>/export.csv" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /files
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /files` — Source: backend\app\routes\scan_results.py

```bash
curl -i -X GET "http://<HOST:PORT>/files" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /files` — Source: backend\app\routes\visibility.py

```bash
curl -i -X GET "http://<HOST:PORT>/files" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /files` — Source: backend\app\routes\scan_results.py

```bash
curl -i -X GET "http://<HOST:PORT>/files" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /files` — Source: backend\app\routes\visibility.py

```bash
curl -i -X GET "http://<HOST:PORT>/files" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /health
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /health` — Source: backend\app\routes\health.py

```bash
curl -i -X GET "http://<HOST:PORT>/health" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /health` — Source: backend\app\routes\health.py

```bash
curl -i -X GET "http://<HOST:PORT>/health" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /healthz
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /healthz` — Source: backend\app\routes\healthz.py

```bash
curl -i -X GET "http://<HOST:PORT>/healthz" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /healthz` — Source: backend\app\routes\healthz.py

```bash
curl -i -X GET "http://<HOST:PORT>/healthz" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /login
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/login` — Steps and fields: Unknown (needs source)
**How to use (API):**
- No API endpoints detected for this prefix.
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /logs
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /logs` — Source: backend\app\routes\logs.py

```bash
curl -i -X GET "http://<HOST:PORT>/logs" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /logs` — Source: backend\app\routes\logs.py

```bash
curl -i -X GET "http://<HOST:PORT>/logs" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /mapping
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /mapping` — Source: backend\app\routes\module_mapping.py

```bash
curl -i -X GET "http://<HOST:PORT>/mapping" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /mapping` — Source: backend\app\routes\module_mapping.py

```bash
curl -i -X GET "http://<HOST:PORT>/mapping" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /me
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `PUT /me` — Source: backend\app\routes\users.py

```bash
curl -i -X PUT "http://<HOST:PORT>/me" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
- `PUT /me` — Source: backend\app\routes\users.py

```bash
curl -i -X PUT "http://<HOST:PORT>/me" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /metrics
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /metrics` — Source: backend\app\routes\metrics.py

```bash
curl -i -X GET "http://<HOST:PORT>/metrics" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /metrics` — Source: backend\app\routes\metrics.py

```bash
curl -i -X GET "http://<HOST:PORT>/metrics" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /parent
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/parent` — Steps and fields: Unknown (needs source)
**How to use (API):**
- No API endpoints detected for this prefix.
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /posts
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/posts/:postId` — Steps and fields: Unknown (needs source)
**How to use (API):**
- No API endpoints detected for this prefix.
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /root-sibling
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- Navigate to `/root-sibling` — Steps and fields: Unknown (needs source)
**How to use (API):**
- No API endpoints detected for this prefix.
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /trends
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /trends` — Source: backend\app\routes\compliance.py

```bash
curl -i -X GET "http://<HOST:PORT>/trends" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /trends` — Source: backend\app\routes\compliance.py

```bash
curl -i -X GET "http://<HOST:PORT>/trends" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /users
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /users` — Source: backend\app\routes\users_admin.py

```bash
curl -i -X GET "http://<HOST:PORT>/users" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /users` — Source: backend\app\routes\users_admin.py

```bash
curl -i -X GET "http://<HOST:PORT>/users" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /users/me` — Source: backend\app\routes\users_me.py

```bash
curl -i -X GET "http://<HOST:PORT>/users/me" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /users/me` — Source: backend\app\routes\users_me.py

```bash
curl -i -X GET "http://<HOST:PORT>/users/me" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /zip
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `GET /zip` — Source: backend\app\routes\export.py

```bash
curl -i -X GET "http://<HOST:PORT>/zip" \
  -H "Authorization: Bearer <JWT>" 
```
- `GET /zip` — Source: backend\app\routes\export.py

```bash
curl -i -X GET "http://<HOST:PORT>/zip" \
  -H "Authorization: Bearer <JWT>" 
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

### Feature: /{agent_id}
**Phase:** Unknown (needs source)
**Purpose:** Unknown (needs source)
**Who can use (roles):** Unknown (needs source)
**Prerequisites:**
- Env keys referenced in code relevant to this feature: Unknown (needs source)
- DB migrations required: Refer to Alembic list above
- Seeds: Refer to seed scripts above
**How to use (UI):**
- No UI routes detected for this prefix.
**How to use (API):**
- `POST /{agent_id}/logs` — Source: backend\app\routes\agent_logs.py

```bash
curl -i -X POST "http://<HOST:PORT>/{agent_id}/logs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
- `POST /{agent_id}/logs` — Source: backend\app\routes\agent_logs.py

```bash
curl -i -X POST "http://<HOST:PORT>/{agent_id}/logs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  --data '{}'
```
**Troubleshooting:**
- Check network tab / console for errors (UI).
- Verify JWT and CORS origins if 401/403/blocked preflight. Evidence files listed above.
- Check backend logs for the route handler file shown above.
**Validation checklist:**
- Page renders without console errors (UI).
- Endpoint returns expected HTTP status (2xx/4xx) with valid JSON (API).
- Audit/log entries created if applicable (Unknown — needs source).

## 5. Auth & RBAC Quick‑Starts
- **Login page/route:** Derived from UI routes containing `/login` if present.
  - Detected: /login
- **Post‑login landing (dashboard):** Routes containing `/dashboard` if present.
  - Detected: /dashboard
- **Protected routes check:** try direct navigation to protected paths; expect redirect to `/login` if unauthenticated. Evidence in code: RBAC/JWT hints above.

## 6. CORS & Rate‑Limit
- **CORS configuration files:** See hints in section 1 (exact files listed).
- **Rate‑limit:** Unknown (needs source) unless a rate limiter is present in code.

## 7. Notifications / Workers
- Worker/scheduler files detected:
  - None found
- Retry/backoff policies: Unknown (needs source).

## 8. Logs & Metrics
- Health endpoints detected: /health
- Metrics endpoints detected: /metrics
- Prometheus config files (if any) found in the repository (see Step 2 outputs).

## 9. Data Effects
- For each API call, check handler source files listed in Section 3 to infer DB models, audit logs, and emitted events. This manual lists paths; semantics are **Unknown (needs source)** when not explicit in code comments.

## 10. Troubleshooting — Global
- **401/403:** Confirm JWT token validity and CORS origin whitelist where configured.
- **404:** Verify route exists in Section 3 and correct base URL.
- **500:** Inspect backend logs; trace to the handler file listed for the endpoint.
- **DB errors:** Apply Alembic migrations; confirm DB creds from env keys in Section 1.

## 11. Validation — A1–E22 (Auth & Redirect Lifecycle)
Run through your standard A1–E22 checks against the detected login and dashboard routes above. Ensure protected routes enforce redirects when unauthenticated and respect role permissions where implemented.
