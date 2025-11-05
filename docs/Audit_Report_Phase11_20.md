# Tenantra Platform – Full Audit (Phases 11–20)

This audit reviews the current repository across schema, backend, frontend, workers, observability (Grafana/Prometheus), and DB migrations, focusing on logic sequencing and feature completeness versus the roadmap in `docs/Phase11-20_Deliverable_Tasks.md`.

## Executive Summary

- Core backend models, routes, migrations, and workers are present and map well to Phases 11–20 (integrity, services/tasks snapshots, threat intel, compliance expansion, retention/exports, MSP billing, scan orchestration, audit logs, notification history, cloud discovery).
- Docker Compose, Prometheus, and Grafana provisioning are in place and wired to the backend metrics endpoint.
- Frontend is broadly implemented with many pages and E2E tests. A few integration gaps and minor defects were identified and corrected in this audit.
- The main structural misalignment is the “notification settings” data model, which does not represent tenant alert preferences; it duplicates notification-like fields. A refactor is recommended.

## What’s Present (By Area)

- Schema & DB
  - Alembic migrations include a unified base and explicit tables for phases (e.g., `T_002_phase11_20_tables.py`, audit, scheduled scans, registry/services/tasks snapshots).
  - Models exist for integrity (`registry_snapshot`, `boot_config`, `integrity_event`), runtime (`process_snapshot`, baselines), TI (`ioc_feed`, `ioc_hit`), billing (`billing_plan`, `usage_log`, `invoice`), scans (`scan_job`, `scan_result`, `scheduled_scan`), notifications (`notification`, `notification_log`).

- Backend & Workers
  - FastAPI app mounts routes for health, auth, users/roles/tenants, modules/runs/schedules, compliance, assets/visibility, notifications (inbox + history + settings), audit logs, billing, scan orchestration, observability admin and public settings.
  - Prometheus metrics endpoint (`/metrics`) and HTTP middleware latency/counter collectors.
  - Workers: notifications worker (opt-in) and module scheduler worker with safe polling/commit cycles.

- Frontend
  - React + Vite + Tailwind; pages for Dashboard, Profile, Compliance Trends/Matrix, Notifications, Notification History, Process Monitoring, Persistence, Threat Intel, Retention/Exports, Billing, Scan Orchestration, Module Catalog, Cloud Discovery, Discovery, Admin Settings, Observability Setup, FAQ.
  - Auth context + role gating, common API helper with JWT + `X-Tenant-Id` propagation, shell layout with dynamic nav and tenant switcher for admins.
  - E2E tests exist for module catalog filtering and process monitoring.

- Observability
  - Prometheus config scrapes backend `backend:5000/metrics`.
  - Grafana provisioning includes Tenantra overview and integrity dashboards; public settings endpoint exposes `grafana.url`, `dashboard_uid`, and `datasource_uid`.

## Issues Found And Fixes Applied

1) Frontend route artifact in `src/App.jsx`
   - Symptom: Stray `<Route path="onboarding" .../>` JSX after the component closing brace, likely breaking the build.
   - Fix: Moved onboarding route inside `/app` section and removed stray lines.
   - File: frontend/src/App.jsx

2) Notifications page stubbed
   - Symptom: `src/pages/Notifications.jsx` had a TODO and never fetched real data.
   - Fix: Implemented GET `/notifications` via `lib/api` and rendered results safely.
   - File: frontend/src/pages/Notifications.jsx

3) Alert Settings endpoint mismatch
   - Symptom: `src/pages/AlertSettings.jsx` called `/alertsettings` which the backend does not expose.
   - Fix: Aligned to GET `/notifications/settings` and added basic table rendering.
   - Note: This page is not currently routed in the app. Consider adding a menu entry under Signals/Admin when the model is corrected (see below).
   - File: frontend/src/pages/AlertSettings.jsx

4) Minor UI placeholders
   - Symptom: `NotificationHistory.jsx` used replacement glyphs (�) for empty values.
   - Recommendation: Replace with `-` for clarity. Encoding of the current file prevented automated patch; suggest re-saving as UTF-8 and replacing the placeholders during the next frontend change.
   - File: frontend/src/pages/NotificationHistory.jsx

## Structural Gaps And Recommended Changes

1) Redesign Notification Settings Model (Priority: High)
   - Current state: `models/notification_setting.py` stores fields like `title`, `message`, `status`, `severity`, `sent_at` — these mirror notifications, not “settings”.
   - Recommended:
     - Replace with a true preferences/config model, e.g. `notification_prefs`:
       - tenant_id (FK), user_id (FK, nullable for tenant-wide defaults)
       - channels: JSON (enabled channels per event)
       - events: JSON or explicit boolean columns for common events (scan_failed, compliance_violation, agent_offline, threshold_breach, etc.)
       - throttle windows, digest options (immediate, hourly digest, daily digest)
     - Add Pydantic schemas and CRUD routes that read/write preferences (separate from send logs and templates).
     - Migrate existing table or introduce new one and deprecate `notification_settings` to avoid data confusion.

2) Feature Flags Bootstrap API (Priority: Medium)
   - Current state: Sidebar uses `getLocalFeatures()` only. Some pages are hidden unless toggled manually.
   - Recommended: Add a backend `/features` endpoint that returns feature flags per tenant/role from `app_settings` or a static map, then hydrate the frontend on boot to enable relevant nav items.

3) Frontend Consistency Cleanups (Priority: Medium)
   - Remove duplicate file `frontend/src/services/userService.js-1`.
   - Ensure all pages referenced by nav exist and vice versa; decide whether to expose Alert Settings in the UI once the model is corrected.
   - Re-save `NotificationHistory.jsx` as UTF-8 and replace placeholder glyphs; add basic pagination/filters (query params exist on backend).

4) Backend Hygiene (Priority: Low)
   - Remove stray files: `backend/app/main.py.PATCH_S17` and any `*.README_S*` markers that are not needed.
   - Consider exposing a health summary endpoint that includes worker status (notifications, scheduler) for quick operational checks (beyond `/health`).

5) Observability Enhancements (Priority: Low)
   - Add application-specific counters (e.g., notifications sent/failed, scheduled runs executed, audit log writes) to Prometheus.
   - Ensure Grafana dashboards reference the exact metric names exposed in `observability/metrics.py` and any new metrics you add.

## Roadmap Alignment (Phases 11–20)

- Phase 11–12 (Registry/Boot/Services/Tasks):
  - Models present (`registry_snapshot`, `boot_config`, `service_snapshot`, `task_snapshot`), plus baselines.
  - Frontend pages: `Persistence.jsx` and `Integrity.jsx` cover registry/services/boot workflows.
  - Recommendation: Validate diffs/baselines UX and add CSV exports if needed.

- Phase 13 (Threat Intelligence):
  - Models present (`ioc_feed`, `ioc_hit`), routes exist.
  - Frontend page `ThreatIntel.jsx` present. Confirm feed sync jobs and API keys management via `app_settings` or secrets.

- Phase 14 (Compliance Control Expansion):
  - Compliance routes and export present; matrix page exists.
  - Recommendation: Ensure mapping import/export via CSV in admin flows.

- Phase 15 (Retention & Data Export):
  - `retention_policy` model and `export` routes exist; frontend `RetentionExports.jsx` present.
  - Recommendation: Validate purge jobs via a periodic worker and S3-like archival if used.

- Phase 16 (MSP Control & Billing):
  - `billing_plan`, `usage_log`, `invoice` present; routes for plans/usage/invoices; frontend `Billing.jsx` wired.
  - Recommendation: Add role gates in UI, and simple invoice PDF rendering if not already in place.

- Phase 17 (Scan Orchestration):
  - `scan_job`, `scan_result` present; routes for jobs/results; page `ScanOrchestration.jsx` present; scheduler worker exists for module schedules.
  - Recommendation: Add job queueing metrics and a global status dashboard.

- Phase 18 (Audit Log System):
  - `audit_logs` model and routes present; frontend not directly linked in nav by default (flagged).
  - Recommendation: Expose basic viewer with filters and tie export buttons to backend.

- Phase 19 (Notification History):
  - `notification_log` present with read/create routes; `NotificationHistory.jsx` implemented.
  - Recommendation: Pagination and export, plus correlation to associated `notification` records.

- Phase 20 (Cloud & Hybrid Discovery):
  - `cloud_account` model present; routes `cloud.py` exist; page `CloudDiscovery.jsx` present.
  - Recommendation: Add credential storage policy and rate limiting for provider APIs.

## Action Plan (Prioritized)

1) Refactor “Notification Settings” into true preferences (schema, routes, UI) [High]
2) Add `/features` bootstrap endpoint and hydrate sidebar features dynamically [Medium]
3) Clean frontend build issues (encoding, duplicate files, minor dead code) [Medium]
4) Add operational health and metrics (worker status, domain counters) [Low]
5) Remove repo artifacts and consolidate README markers [Low]

---

Changes applied in this audit:
- Fixed Notifications page to consume `/notifications`.
- Fixed router artifact and added `/app/onboarding` route placement.
- Aligned Alert Settings page to `/notifications/settings` (read-only view for now).
- Noted Notification History encoding issue (manual UTF-8 save suggested next change).

