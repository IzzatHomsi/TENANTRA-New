# Tenantra Development Sprints

**IMPORTANT:** At the end of each sprint, ensure `docs/Tenantra_Master_Brain_v1.0.md` is updated with all relevant details.

This document organizes all development tasks into focused sprints to provide a clear roadmap for improving the Tenantra application.

---

## Sprint 1: Critical Security & Stability

**Goal:** Address all critical security vulnerabilities and fix major application-breaking bugs to stabilize the platform. This sprint is foundational for all future work.

### P1.1: Secure Application Secrets & Credentials

*   **Task:** Remove hardcoded development encryption key and insecure fallback.
    *   **Issue:** A hardcoded development encryption key is used as a fallback in `backend/app/core/secrets.py`. If the `TENANTRA_ENC_KEY` and `JWT_SECRET` environment variables are not set, this insecure key could be used in a production environment.
    *   **Severity:** High
    *   **Action:**
        1.  Refactor `get_enc_key()` in `backend/app/core/secrets.py` to remove the hardcoded fallback key and the logic that allows the `JWT_SECRET` to be used as the encryption key.
        2.  The application should raise a `RuntimeError` on startup if `TENANTRA_ENC_KEY` is not set in a non-test environment.
    *   **Files to check:**
        *   `backend/app/core/secrets.py`

*   **Task:** Remove all hardcoded credentials.
    *   **Issue:** Hardcoded default passwords (e.g., the legacy admin password) and other secrets are present in multiple scripts, test files, and configuration files, posing a significant security risk.
    *   **Severity:** High
    *   **Action:**
        1.  Remove all hardcoded credentials from the codebase.
        2.  Use environment variables or a secure secret management system to manage all secrets.
        3.  For development, provide a `.env.example` file that developers can copy and fill in.
        4.  Ensure the seeding script either generates a random password or requires one to be set via an environment variable.
    *   **Files to check:**
        *   `tenantra_control_menu.ps1_old`
        *   `scripts/db_seed.py`
        *   `backend/app/scripts/db_seed.py`
        *   `backend/app/bootstrap.py`
        *   `backend/dev_server.py`
        *   `backend/app/core/security.py`

*   **Task:** Consolidate and secure JWT secret management.
    *   **Issue:** The backend has duplicate and confusing JWT secret loading logic, including a hardcoded secret in the development server.
    *   **Severity:** Medium
    *   **Action:**
        1.  Standardize on the implementation in `backend/app/core/security.py` (`load_jwt_secret`).
        2.  Remove the unused `get_jwt_secret` function from `backend/app/core/secrets.py`.
        3.  Remove the hardcoded JWT secret from `backend/dev_server.py`.
    *   **Files to check:**
        *   `backend/app/core/secrets.py`
        *   `backend/app/core/security.py`
        *   `backend/dev_server.py`

### P1.2: Fix Critical 500 Errors

*   **Task:** Resolve Audit Log 500 error.
    *   **Issue:** The "Audit Logs" page and the "Audits" tab in Admin Settings both show a 500 Internal Server Error.
    *   **Root Cause:** The error is in the backend, likely due to a model serialization failure in the `AuditLog` model or an unhandled exception in the `decrypt_data` function.
    *   **Action:**
        1.  Investigate and resolve the serialization issue in `backend/app/models/audit_log.py`.
        2.  Ensure `decrypt_data` has robust error handling.
    *   **Files to check:**
        *   `backend/app/routes/audit_logs.py`
        *   `backend/app/models/audit_log.py`

*   **Task:** Resolve Alert Settings 500 error.
    *   **Issue:** Saving changes on the "Alert Settings" page results in a 500 error.
    *   **Root Cause:** The `PUT /notification-prefs` endpoint is failing, likely due to a database schema mismatch where the `channels` and `events` columns in the `notification_prefs` table are not JSON-compatible types.
    *   **Action:**
        1.  Verify the database schema for the `notification_prefs` table and ensure the `channels` and `events` columns are `JSON` or `JSONB`.
        2.  Check the Alembic migrations to ensure the table is created correctly.
    *   **Files to check:**
        *   `backend/app/routes/notification_prefs.py`
        *   `backend/app/models/notification_pref.py`
        *   Relevant Alembic migration files.

### P1.3: Patch Access Control & Insecure Logic

*   **Task:** Fix broken access control in data export endpoints.
    *   **Issue:** The `/assets` and `/compliance/export.*` endpoints do not implement tenant-based filtering, allowing users to potentially access data from other tenants.
    *   **Severity:** High
    *   **Action:**
        1.  Modify the `/assets` endpoint in `backend/app/routes/assets.py` to filter assets based on the authenticated user's `tenant_id`.
        2.  Modify the `/compliance/export.csv` and `/compliance/export.pdf` endpoints in `backend/app/routes/compliance_export.py` to filter results based on the authenticated user's `tenant_id`.
    *   **Files to check:**
        *   `backend/app/routes/assets.py`
        *   `backend/app/routes/compliance_export.py`

*   **Task:** Disable insecure CSV module loading by default.
    *   **Issue:** The feature that loads modules from a CSV file at startup in `backend/app/main.py` (`_maybe_import_modules`) presents a significant security risk if the CSV file can be modified by an attacker.
    *   **Severity:** Medium
    *   **Action:** This feature should be disabled by default, made opt-in, and protected.
    *   **Files to check:**
        *   `backend/app/main.py`

*   **Task:** Address insecure exposure of the backend service.
    *   **Issue:** The `docker-compose.override.expose.yml` file exposes the backend service to all network interfaces (`0.0.0.0`), which could allow unauthorized access.
    *   **Severity:** High
    *   **Action:** The documentation should be updated to clearly state the security implications of using this file and recommend more secure alternatives for development.
    *   **Files to check:**
        *   `docker/docker-compose.override.expose.yml`

### P1.4: Fix Critical Auth & Authorization Gaps
*   **Task:** Unify Current User Object to Prevent Stale Permissions.
    *   **Issue:** The application uses two different "current user" objects. The main `get_current_user` dependency creates a user object from the JWT payload without consulting the database. This means changes to a user's role or status in the database are not reflected until their token expires.
    *   **Severity:** Critical
    *   **Action:** Refactor the `get_current_user` dependency in `backend/app/dependencies/auth.py` to fetch the user from the database using the `user_id` from the token on every request. This ensures that all permission checks use the user's current, authoritative state.
    *   **Files to check:**
        *   `backend/app/dependencies/auth.py`
        *   `backend/app/routes/auth.py`

*   **Task:** Implement Secure Password Reset Flow.
    *   **Issue:** The application provides no way for users to reset a forgotten password. This is a fundamental feature for user management.
    *   **Severity:** High
    *   **Action:**
        1.  Create a new endpoint (e.g., `/auth/forgot-password`) that takes a username or email.
        2.  Generate a secure, single-use, time-limited token and send it to the user's registered email address.
        3.  Create a second endpoint (e.g., `/auth/reset-password`) that allows the user to set a new password if they provide a valid token.
    *   **Files to check:**
        *   `backend/app/routes/auth.py` (new endpoints)
        *   `backend/app/core/security.py` (new token generation logic)
        *   `backend/app/utils/email.py` (to send the email)

*   **Task:** Implement JWT Revocation on Logout.
    *   **Issue:** The application does not invalidate JWTs on logout. An old token can be reused until it expires, even after the user has logged out.
    *   **Severity:** Medium
    *   **Action:**
        1.  Create a `revoked_tokens` table in the database to store the `jti` (JWT ID) of logged-out tokens.
        2.  Add a `jti` claim to all new JWTs.
        3.  On logout, add the token's `jti` to the `revoked_tokens` table.
        4.  Modify the `get_current_user` dependency to check if the token's `jti` is in the revoked list.
    *   **Files to check:**
        *   `backend/app/dependencies/auth.py`
        *   `backend/app/routes/auth.py`
        *   `backend/app/models/` (new model for revoked tokens)

*   **Task:** Standardize Authorization Logic Across All Routes.
    *   **Issue:** Authorization logic is inconsistent. Some routes use `_ensure_admin`, others use `_resolve_tenant`, and others have no checks at all. This makes the application difficult to audit and maintain.
    *   **Severity:** High
    *   **Action:**
        1.  Refactor all authorization logic to use the FastAPI dependency injection system.
        2.  Create a set of standard, reusable dependencies in `core/permissions.py` (e.g., `require_admin`, `require_tenant_scope`).
        3.  Replace all manual and inconsistent checks (`_ensure_admin`, `_resolve_tenant`) with these standard dependencies.
        4.  Refactor `get_admin_user` and `get_settings_user` in `backend/app/core/auth.py` to use `get_current_user` and eliminate duplicate code.
        5.  Review and correct the authorization logic in `alerts.py`, `schedules.py`, and `scan_results.py` to ensure tenant users can manage their own resources.
    *   **Files to check:**
        *   `backend/app/routes/schedules.py`
        *   `backend/app/routes/scan_orchestration.py`
        *   All files in `backend/app/routes/`

### P1.5: Secure Agent Communication Channel
*   **Task:** Implement Agent-Side Authentication.
    *   **Issue:** Agents are issued tokens upon creation, but there are no agent-facing endpoints that require or validate these tokens. This means there is no agent authentication, allowing any unauthenticated party to potentially interact with agent-related APIs.
    *   **Severity:** Critical
    *   **Action:**
        1.  Create a new FastAPI dependency (`get_current_agent`) that validates an agent token from a request header (e.g., `X-Agent-Token`).
        2.  Apply this dependency to all agent-facing endpoints, such as configuration retrieval and scan result submission.
        3.  Ensure that the agent's tenant is checked to prevent cross-tenant data leakage.
    *   **Files to check:**
        *   `backend/app/routes/agents.py`
        *   `backend/app/dependencies/` (new dependency file)

*   **Task:** Harden Agent Token Storage and Validation.
    *   **Issue:** Agent tokens are stored in plaintext in the database and validated with a direct string comparison, making them vulnerable to theft and timing attacks.
    *   **Severity:** Critical
    *   **Action:**
        1.  When an agent token is created, store a hash of the token in the `agents.token` column instead of the raw token.
        2.  In the `verify_agent_token` dependency, hash the incoming token from the `X-Agent-Token` header.
        3.  Use a constant-time comparison function (e.g., `secrets.compare_digest`) to compare the hashed incoming token with the hashed token from the database.
    *   **Files to check:**
        *   `backend/app/dependencies/agents.py`
        *   `backend/app/services/agent_enrollment.py`

*   **Task:** Create a Secure Agent Self-Registration/Enrollment Flow.
    *   **Issue:** The current agent "enrollment" is an admin-only action. There is no secure workflow for a new agent instance to automatically enroll itself with the backend, making deployment manual and cumbersome.
    *   **Severity:** Medium
    *   **Action:**
        1.  Design a two-stage enrollment process. Stage 1: An admin generates a single-use enrollment token in the UI.
        2.  Stage 2: Create a new public endpoint (e.g., `/agents/enroll/self`) where an agent can present the enrollment token.
        3.  Upon successful validation of the enrollment token, the backend creates the new agent and returns a persistent agent-specific API token.
    *   **Files to check:**
        *   `backend/app/routes/agents.py`
        *   `backend/app/routes/agents_admin.py`

### Test Plan
*   **Secrets & Credentials:**
    *   Verify that the backend fails to start if the `TENANTRA_ENC_KEY` environment variable is not set.
    *   Verify that no hardcoded passwords (like the legacy admin default) exist anywhere in the codebase.
    *   Verify that the database seeding script fails or prompts for a password if one is not provided via environment variables.
*   **Critical Errors:**
    *   Verify that the "Audit Logs" page and the "Audits" tab in Admin Settings load correctly without any 500 errors.
    *   Verify that changes can be saved on the "Alert Settings" page without triggering a 500 error.
*   **Access Control:**
    *   Create two tenants (Tenant A and Tenant B) and a user for each. Log in as Tenant A's user and attempt to export assets or compliance data for Tenant B. Verify the request is denied.
    *   Verify that the application starts and runs correctly with the CSV module import feature disabled by default.
*   **Authentication & Authorization:**
    *   As an admin, demote another admin user to a standard user role. Verify that the demoted user immediately loses access to admin-only pages and API endpoints without needing to log out and log back in.
    *   Log out of the application. Using the now-expired JWT, attempt to access a protected endpoint (e.g., `/users/me`). Verify the request is rejected with a 401 Unauthorized error.
    *   Verify that the password reset flow is fully functional: a user can request a reset link, receive an email, and successfully update their password.
*   **Agent Security:**
    *   Attempt to access an agent-facing endpoint (e.g., for configuration) without a valid `X-Agent-Token`. Verify the request is denied.
    *   Use the new enrollment flow to generate a single-use token, have a new agent use it to enroll, and verify the agent receives a persistent API token.
    *   Inspect the database to confirm that agent tokens are stored as hashes, not plaintext.

---

## Sprint 2: Database & Backend Health

**Goal:** Remediate widespread inconsistencies in the database schema, fix unsafe migrations, and resolve backend dependency issues to improve data integrity and reliability.

### P2.1: Stabilize Database Schema
*   **Issue:** The database models and schema suffer from widespread inconsistencies, missing best practices, and code duplication.
*   **Tasks:**
    1.  **Standardize on Mixins:** Refactor all models to use `TimestampMixin` and `ModelMixin` for consistent `created_at`/`updated_at` fields and helper methods.
    2.  **Add Missing Indexes:** Audit all models and ensure every `ForeignKey` column has `index=True`.
    3.  **Consolidate Notification Models:** Review and consolidate the overlapping `Notification`, `NotificationSetting`, and `NotificationPreference` models.
    4.  **Standardize on `JSONB`:** Refactor all models to use the PostgreSQL `JSONB` type for better performance.
    5.  **Enforce Cascade Deletes:** Audit all relationships and add `ondelete="CASCADE"` to foreign keys where appropriate to prevent orphaned rows.
    6.  **Simplify Module Status:** Refactor the `Module` model to use a single `status` field (ideally an `Enum`) instead of the confusing `enabled` and `status` fields.
    7.  **Add `revoked_tokens` Table:** Create a new table to support JWT revocation.
*   **Files to check:**
    *   All files in `backend/app/models/`

### P2.2: Harden Migrations & Data Seeding
*   **Issue:** The Alembic migrations are not consistently safe or idempotent, and they contain database-specific code and inconsistent default values.
*   **Tasks:**
    1.  **Make Migrations Idempotent:** Review and refactor migrations to be safely re-runnable.
    2.  **Standardize Timestamp Defaults:** Update all migrations to use a single, timezone-aware default like `server_default=sa.text("timezone('utc', now())")`.
    3.  **Remove DB-Specific Code:** Fix migrations that contain database-specific casts or functions.
    4.  **Clean Up Migration History:** Investigate and remove the `backend/alembic/versions/_archive` directory if the migrations are obsolete.
*   **Files to check:**
    *   All files in `backend/alembic/versions/`

### P2.3: Resolve Backend Dependencies & Logic
*   **Issue:** The project's Python dependencies are not managed securely or robustly.
*   **Tasks:**
    1.  **Resolve Conflicting DB Drivers:** Remove `psycopg2-binary` from `backend/requirements.txt` to standardize on `psycopg[binary]`.
    2.  **Address Vulnerable `fpdf`:** Replace the `fpdf` library with a more secure and actively maintained library like `reportlab` or `WeasyPrint`.
    3.  **Pin Dependencies:** Pin all dependency versions in `backend/requirements.txt` to specific, known-good versions.
*   **Files to check:**
    *   `backend/requirements.txt`

*   **Issue:** The CORS handling is overly complex and could lead to misconfiguration.
*   **Task:** Simplify CORS configuration by removing the manual preflight handler in `backend/app/routes/auth.py` and centralizing all logic in the `DynamicCORSMiddleware`.
*   **Files to check:**
    *   `backend/app/routes/auth.py`
    *   `backend/app/middleware/dynamic_cors.py`

### P2.4: Refactor Multi-Tenancy Enforcement
*   **Task:** Fix Flawed Tenant Scope Check.
    *   **Issue:** The `require_tenant_scope` dependency in `core/permissions.py` contains flawed logic that only checks for tenant mismatches for admin users, potentially allowing standard users to access resources from other tenants.
    *   **Severity:** High
    *   **Action:** Rewrite the `require_tenant_scope` logic to enforce tenant isolation for all users by default. It should ensure that a user's `tenant_id` matches the `tenant_id` of the resource they are trying to access.
    *   **Files to check:**
        *   `backend/app/core/permissions.py`

*   **Task:** Create and Apply a Global Tenant Requirement Dependency.
    *   **Issue:** Tenant-scoping is not applied consistently. Checks are either missing or implemented as one-off logic within specific routes.
    *   **Severity:** High
    *   **Action:**
        1.  Create a new, generic FastAPI dependency that extracts a `tenant_id` from a resource and verifies the current user belongs to that tenant.
        2.  Systematically audit all API routes and apply this dependency to every endpoint that accesses tenant-scoped data (e.g., assets, compliance results, agents, etc.).
    *   **Files to check:**
        *   `backend/app/dependencies/auth.py` (or a new `tenancy.py`)
        *   All files in `backend/app/routes/`

### P2.5: Overhaul Background Task Architecture
*   **Task:** Replace Custom Threading Workers with a Robust Task Queue.
    *   **Issue:** The application uses a custom, in-process `threading.Thread` model for background workers. This architecture is not scalable, not persistent, and prone to race conditions in any multi-process environment (like production).
    *   **Severity:** Critical
    *   **Action:**
        1.  Integrate a mature, production-ready task queue library like Celery with a Redis or RabbitMQ broker.
        2.  Refactor the logic from `worker/module_scheduler.py` and `worker/notifications_worker.py` into Celery tasks.
        3.  Remove the custom `threading.Thread` worker implementations.
        4.  Update the `docker-compose.yml` to include a Celery worker service and a message broker service.
    *   **Files to check:**
        *   `backend/app/worker/`
        *   `backend/app/main.py` (remove worker startup/shutdown)
        *   `docker-compose.yml`

*   **Task:** Implement Database-Level Locking for Job Processing.
    *   **Issue:** The current scheduler fetches jobs with a simple `SELECT ... LIMIT`, which can lead to multiple workers picking up the same job in a race condition.
    *   **Severity:** High
    *   **Action:** When fetching jobs from the database, use `SELECT ... FOR UPDATE SKIP LOCKED` to ensure that each job is transactionally locked and processed by only one worker instance.
    *   **Files to check:**
        *   `backend/app/worker/module_scheduler.py` (or its replacement Celery task)

### Test Plan
*   **Database Schema:**
    *   Inspect the database schema to confirm that all models have `created_at` and `updated_at` columns, foreign keys are indexed, and `JSON` columns have been migrated to `JSONB`.
    *   Verify that deleting a tenant record correctly cascades to delete all associated users, agents, and other resources.
*   **Migrations & Dependencies:**
    *   Run all Alembic migrations from a clean database to the latest version and confirm they complete without errors. Run them a second time to ensure they are idempotent.
    *   Verify that PDF reports can be generated successfully using the new, more secure PDF library.
    *   Check `backend/requirements.txt` to ensure all dependencies are pinned to specific versions.
*   **Multi-Tenancy:**
    *   Write an integration test where a standard user from Tenant A attempts to access a resource (e.g., an agent) belonging to Tenant B by its ID. Verify the request is denied with a 403 or 404 error.
*   **Background Tasks:**
    *   Verify that the old `threading.Thread` worker code has been completely removed.
    *   Schedule a new scan and confirm that a Celery task is created and processed by a Celery worker.
    *   Run multiple Celery worker instances and schedule several jobs simultaneously. Verify that each job is processed only once, confirming that the `SELECT ... FOR UPDATE SKIP LOCKED` logic is working correctly.

---

## Sprint 3: Developer Experience & Testing

**Goal:** Improve the developer workflow, consolidate the testing strategy, and create clear, accessible documentation to accelerate future development.

### P3.1: Consolidate Testing Strategy
*   **Issue:** The repository contains numerous E2E and smoke tests, but it is unclear if they are consistently run or passing.
*   **Tasks:**
    1.  **Consolidate Test Execution:** Create a single, top-level script or `Makefile` command (e.g., `make test-all`) that runs all backend, frontend, and E2E tests.
    2.  **Fix Failing E2E Tests:** The `process_monitoring.spec.ts` and `integrity.spec.ts` tests are likely broken. Audit and fix them.
    3.  **CI Integration:** Ensure the consolidated test command is integrated into the CI/CD pipeline to run on every pull request.

### P3.2: Improve Documentation
*   **Issue:** While there is a lot of documentation, it is scattered and may be out of date.
*   **Tasks:**
    1.  **Create a Central `RUNBOOK.md`:** Consolidate critical operational instructions into a single `docs/RUNBOOK.md`.
    2.  **Update `README.md`:** Update the root `README.md` to be a concise entry point that links to other key documents.
    3.  **Document Environment Variables:** Create a `.env.example` file in the root directory that lists all required environment variables.

### P3.3: Streamline Build Process
*   **Issue:** The frontend build process has multiple, potentially conflicting Vite configurations.
*   **Task:** Consolidate `vite.config.js`, `vite.catalog-remote.config.js`, and `vite.ssr.config.js` into a single, well-documented `vite.config.js`.

### Test Plan
*   **Testing Strategy:**
    *   Execute the new `make test-all` command and verify that it runs all backend unit tests, frontend unit tests, and Playwright E2E tests, and that all tests pass.
    *   Check the CI configuration file to ensure that this consolidated test command is configured to run on every new pull request.
*   **Documentation:**
    *   Verify that a `docs/RUNBOOK.md` file exists and contains essential operational procedures.
    *   Verify that a `.env.example` file exists at the root of the project and documents all necessary environment variables for development.
*   **Build Process:**
    *   Delete the old, separate Vite configuration files.
    *   Run the frontend build (`npm run build`) and development server (`npm run dev`) and verify that both processes complete successfully using the new unified `vite.config.js`.

---

## Sprint 4: UI/UX Polish & Feature Completion

**Goal:** Address all remaining UI/UX inconsistencies, fix frontend-related bugs, and complete partially implemented features to deliver a more polished user experience.

### P4.1: Fix UI/UX Inconsistencies
*   **Issue:** The application's styling is inconsistent, with readability issues and unprofessional references.
*   **Tasks:**
    1.  **Fix Light Theme:** Replace hardcoded Tailwind CSS color classes with theme variables.
    2.  **Standardize Admin Settings:** Refactor `frontend/src/pages/AdminSettings.jsx` to use theme variables.
    3.  **Remove "Facebook" References:** Remove all "facebook" and "fb" references from the codebase.
*   **Files to check:**
    *   `frontend/src/styles/theme.css`, `frontend/src/pages/AdminSettings.jsx`, `frontend/src/layouts/Shell.jsx`

*   **Issue:** The main navigation could be more intuitive.
*   **Task:** Move the "My Profile" and "Feature Flags" links from the main sidebar to the settings dropdown menu.
*   **Files to check:**
    *   `frontend/src/layouts/Shell.jsx`

### P4.2: Resolve Frontend Bugs & Onboarding Issues
*   **Issue:** The auth status indicator is a hidden debug feature.
*   **Task:** Convert the debug widget into a user-facing API connection status indicator.
*   **Files to check:**
    *   `frontend/src/layouts/Shell.jsx`

*   **Issue:** The "Compliance Matrix" and "Retention & Exports" pages show 400 Bad Request errors.
*   **Root Cause:** Backend endpoints are being called without a required `tenant_id` query parameter.
*   **Task:** Update `frontend/src/pages/ComplianceMatrix.jsx` and `frontend/src/pages/RetentionExports.jsx` to send the `tenant_id`.
*   **Files to check:**
    *   `frontend/src/pages/ComplianceMatrix.jsx`, `frontend/src/pages/RetentionExports.jsx`

### P4.3: Complete Unfinished Features
*   **Issue:** The "Compliance Trends" page shows static placeholder data.
*   **Task:** Create a backend endpoint to provide real data and update `frontend/src/pages/ComplianceTrends.jsx` to display it.
*   **Files to check:**
    *   `frontend/src/pages/ComplianceTrends.jsx`

*   **Issue:** All modules are enabled by default, and there is no way to configure agents.
*   **Tasks:**
    1.  **Module Status:** Change the default value of the `enabled` column in the `Module` model to `False`.
    2.  **Agent Management:** Create a new "Agent Management" page for listing, creating, and configuring agents.
*   **Files to check:**
    *   `backend/app/models/module.py`

*   **Task:** Implement User Self-Registration Flow.
    *   **Issue:** The application lacks a self-service registration option for new users. This is essential for a SaaS model.
    *   **Severity:** Medium
    *   **Action:**
        1.  Create a new endpoint (e.g., `/auth/register`) that accepts user details.
        2.  Implement logic to create a new user and potentially a new tenant if applicable.
        3.  Consider an email verification step to ensure the user's email is valid.
    *   **Files to check:**
        *   `backend/app/routes/auth.py`
        *   `backend/app/routes/users.py`

*   **Task:** Implement Tenant Update and Delete.
    *   **Issue:** The application provides no way to update or delete tenants.
    *   **Severity:** Medium
    *   **Action:**
        1.  Create a `PUT /admin/tenants/{tenant_id}` endpoint to update tenant details.
        2.  Create a `DELETE /admin/tenants/{tenant_id}` endpoint to delete a tenant.
        3.  Ensure that deleting a tenant cascades to delete all associated resources (users, agents, etc.).
    *   **Files to check:**
        *   `backend/app/routes/tenants_admin.py`

### P4.4: Unify and Complete Scan Scheduling
*   **Task:** Consolidate `ScheduledScan` and `ScanJob` Models.
    *   **Issue:** The application has two conflicting and overlapping models for scheduling: `ScheduledScan` and `ScanJob`. The background worker only acts on `ScheduledScan`, meaning any schedule set on a `ScanJob` is ignored.
    *   **Severity:** Critical
    *   **Action:**
        1.  Deprecate one of the models (likely `ScheduledScan`).
        2.  Migrate all scheduling logic to use a single, unified model (likely `ScanJob`).
        3.  Refactor the UI and background workers to use this single, authoritative model for all scheduling.
    *   **Files to check:**
        *   `backend/app/models/scheduled_scan.py`
        *   `backend/app/models/scan_job.py`
        *   `backend/app/routes/schedules.py`
        *   `backend/app/routes/scan_orchestration.py`
        *   `backend/app/worker/module_scheduler.py`

*   **Task:** Implement Schedule Update.
    *   **Issue:** The application provides no way to update an existing schedule.
    *   **Severity:** Low
    *   **Action:**
        1.  Create a `PUT /schedules/{schedule_id}` endpoint to update an existing schedule.
    *   **Files to check:**
        *   `backend/app/routes/schedules.py`

### P4.5: Fix and Complete Agent/Module Logic
*   **Task:** Fix Broken Module Assignment Logic.
    *   **Issue:** The logic to assign modules to agents is broken. The `GET /agents/config/{agent_id}` endpoint ignores the `ModuleAgentMapping` table, which is the most specific way to control which modules an agent runs.
    *   **Severity:** Critical
    *   **Action:**
        1.  Refactor the `GET /agents/config/{agent_id}` endpoint to use a clear precedence for module enablement:
            a. Check for an entry in `ModuleAgentMapping` first.
            b. If no agent-specific rule exists, fall back to the `TenantModule` setting.
            c. If no tenant-specific rule exists, fall back to the module's default status.
        2.  Ensure the UI for agent management allows for creating and managing these `ModuleAgentMapping` entries.
    *   **Files to check:**
        *   `backend/app/routes/agents.py`
        *   `backend/app/models/module_agent_mapping.py`

*   **Task:** Implement an Endpoint for Agent Scan Result Submission.
    *   **Issue:** There is no API endpoint for an agent to submit its scan results. The entire agent-based scanning workflow is incomplete because the agent has no way to report its findings back to the backend.
    *   **Severity:** Critical
    *   **Action:**
        1.  Create a new endpoint (e.g., `POST /agents/results`).
        2.  This endpoint must require agent authentication (using the token from P1.5).
        3.  The endpoint should accept a payload containing the module name, status, and result details.
        4.  The backend logic should validate this payload and create a `ScanModuleResult` record, correctly associating it with the authenticated agent and its tenant.
    *   **Files to check:**
        *   `backend/app/routes/agents.py` (or a new results route)
        *   `backend/app/services/module_executor.py`

### Test Plan
*   **UI/UX:**
    *   Switch to the light theme and verify that all text is readable and all components are styled correctly.
    *   Verify that all "facebook" or "fb" styling and naming have been removed from the UI and codebase.
    *   Confirm that the "My Profile" and "Feature Flags" navigation links have been moved from the sidebar to the user settings dropdown menu.
*   **Frontend Bugs:**
    *   Verify that the "Compliance Matrix" and "Retention & Exports" pages now load data correctly without any 400 Bad Request errors.
    *   Verify that a user-friendly API connection status indicator is now visible in the UI.
*   **Feature Completion:**
    *   Navigate to the "Compliance Trends" page and verify that it displays dynamic, real data from the backend instead of static placeholders.
    *   Verify that a new "Agent Management" page exists and that it allows for creating, listing, and configuring agents.
    *   Test the complete user self-registration flow: a new user should be able to sign up, verify their email, and log in to the application.
*   **Scheduling & Agent Logic:**
    *   Verify that scan scheduling is now handled by a single, unified data model and that schedules created in the UI are correctly executed by the backend.
    *   Test the module assignment precedence: specifically assign a module to an agent and verify it runs, then remove the specific assignment and enable it for the tenant, and verify it still runs.
    *   Simulate an agent submitting scan results to the new `POST /agents/results` endpoint. Verify that the data is saved correctly and associated with the correct agent and tenant.

---

## Sprint 5: Project Cleanup & New Features

**Goal:** Remove all redundant and unnecessary files from the repository and begin the design and implementation of major new features.

### P5.1: Execute Full Project Cleanup
*   **Issue:** The project contains a large number of files that appear to be redundant, temporary, or part of old workflows.
*   **Task:** Audit and remove all unneeded files from the extensive list in the original "Project Cleanup" section to simplify the repository.
*   **Task:** Remove redundant `core/rbac.py` file.
    *   **Issue:** The `core/rbac.py` file provides a duplicate, and likely unused, implementation of role-checking logic that is already handled by dependencies in `core/permissions.py`.
    *   **Action:** Verify that `core/rbac.py` is not in use and remove it to reduce code duplication and confusion.
    *   **Files to check:**
        *   `backend/app/core/rbac.py`
        *   Search for usages of `has_any_role` or `require_any_role` in the codebase.

### P5.2: Begin New Feature Development
*   **Issue:** The application lacks the ability to sync users from Active Directory.
*   **Task:** This is a major feature request. Begin by creating a design document that covers AD connection configuration, user mapping, sync scheduling, and handling of user lifecycle events.

### Test Plan
*   **Project Cleanup:**
    *   After the cleanup, run all test suites (`make test-all`) to ensure that removing the files did not break any application functionality.
    *   Verify that the `backend/app/core/rbac.py` file has been deleted and that all authorization and role-checking logic still functions as expected.
*   **New Feature Development:**
    *   Verify that a new design document for Active Directory integration has been created in the `docs/` directory.
    *   Review the design document to ensure it covers all key aspects: connection settings, attribute mapping, sync scheduling, and error handling.
