# Repository Guidelines

## Project Structure & Module Organization
Backend FastAPI code lives in `backend/app` (routes, services, models) with Alembic revisions in `backend/alembic/versions`. Tests go in `backend/tests`, mirroring package paths. The Vite/React client resides in `frontend/src` (`pages/`, `components/`, `auth/`); static assets stay in `frontend/public`. Docker Compose manifests live in `docker/`, while operational runbooks and feature-flag notes sit in `docs/`. Automation and one-off helpers reside in `scripts/`, `tools/`, and the root `Makefile`.

## Build, Test, and Development Commands
Bring up the stack with `make up` (optional `DEV=1` for dev overrides) and stop it via `make down`. Apply migrations through `make migrate`, then seed defaults using `make seed`. For API iteration run `cd backend && uvicorn app.main:create_app --factory --reload`. Frontend development uses `cd frontend && npm install && npm run dev -- --host`. Generate artefacts with `make openapi` and run cross-cutting checks via `make validate`.

## Coding Style & Naming Conventions
Python targets 3.11; Ruff (`ruff check backend/app`) and mypy enforce linting and typing, and CI caps lines at 100 characters with space indentation. Prefer Pydantic models for IO contracts and timestamp-prefixed Alembic filenames. Frontend code is ES modules on React 18; keep components PascalCase, hooks camelCase, and environment constants SCREAMING_SNAKE_CASE. ESLint lives in `frontend/.eslintrc.cjs`; run `npx eslint src` before a PR. Tailwind utility classes stay in JSX, with shared tokens in `frontend/src/styles`.

## Testing Guidelines
Run backend tests with `make test` or `cd backend && pytest -q`; update fixtures in `backend/tests/conftest.py` when models change and cover tenant/RBAC paths. Frontend smoke and E2E suites live in `frontend/tests`; execute them via `npm run test:e2e` and retain updated traces when behaviour shifts. When APIs evolve, regenerate `openapi.json` and refresh Postman collections under `postman/`.

## Commit & Pull Request Guidelines
Commits follow the Phase/Batch prefixes in history (e.g., `P3_B5.6: Lock login flow`) plus an imperative summary; rebase to keep history clean. A PR description should state intent, surface risk, attach UI screenshots, and list verification commands (`make test`, `npm run test:e2e`). Link tracker issues, call out migrations, and ensure required workflows (backend-ci, frontend-ci, compose-yaml-lint, secret-scan) are green before requesting review.

## Security & Configuration Tips
Never commit real secrets; use `.env.local` for development and Docker secrets or CI variables for shared environments. Validate new endpoints against tenant isolation helpers such as `role_required` and the dynamic CORS middleware. Before shipping security-sensitive changes, run `make validate` or `python tools/validate_tenantra.py --output-dir reports`.



## Project Overview

This is a web application with a Python-based backend and a JavaScript-based frontend. The application appears to be a multi-tenant platform for managing security and compliance, with features for user management, threat intelligence, compliance monitoring, and more.


🧠 Tenantra – The Unified IT Discovery & Compliance Platform
Overview

Tenantra is a multi-tenant, cloud-ready IT discovery, security, and compliance automation platform.
It continuously scans, inventories, and secures complex IT environments—covering infrastructure, endpoints, networks, identities, configurations, and compliance posture—under a single intelligent dashboard.

The platform combines DevOps, SecOps, and ITIL-aligned management to provide automated visibility, compliance reporting, alerting, and remediation at scale.

⚙️ Core Architecture

Tenantra runs as a containerized SaaS suite built on:

FastAPI (Python) backend with modular REST APIs

React/Vite frontend dashboard

PostgreSQL database

Docker Compose orchestration

Optional integrations: Redis, Prometheus, Grafana, Loki, Vault

Each tenant’s data is fully isolated by schema and RBAC policy.
The system supports Dev, Staging, and Production environments.

🔒 Security Foundation

Encryption: TLS 1.3 for data-in-transit, AES-256 for data-at-rest.

Key Management: Integrated with HashiCorp Vault / Azure Key Vault.

Key rotation every 90 days.

Encrypted key backups stored separately.

Authentication: JWT-based sessions with bcrypt-hashed passwords.

RBAC: Role-based access for admin, standard, and MSP tiers.

Audit Logs & Compliance Trails: Immutable and exportable per tenant.

🧩 Functional Modules (Phases 3 → 23)
Phase	Functional Domain	Description
3	User Management & Profiles	Full CRUD of users, roles, and tenants; profile editing; session tracking.
4	Alerts & Notifications	Configurable alert rules, email templates, and delivery via SMTP/API.
5	Compliance Dashboard & Export	Real-time compliance scoring, CSV/PDF export, benchmark mapping (CIS, NIST, ISO).
6	Agent System & Scheduling	Lightweight agents for Windows/Linux; recurring scans and job scheduling.
7	Module Engine & Mapping	900+ modular scans (network, OS, cloud, security); dynamic module registry.
8	File & Network Visibility	Monitors open ports, shares, file permissions, and network paths.
9	Identity Exposure	Detects privileged accounts, stale users, and insecure AD configurations.
10	Process & Drift Detection	Baselines running processes; detects unauthorized changes.
11	Registry & Boot Integrity	Windows registry audit and secure-boot integrity checks.
12	Services & Task Scheduler	Inventories auto-start services and scheduled tasks for anomalies.
13	Threat Intelligence	Correlates local findings with CVE/MISP threat feeds.
14	Compliance Control Expansion	Adds NIST, HIPAA, ISO 27001 mappings and rule automation.
15	Retention & Data Export	Data lifecycle policies, archiving, and export management.
16	MSP Control & Billing	Tenant-level feature control, cost tracking, automated invoicing.
17	Scan Orchestration	Parallelized task orchestration across multiple agents/environments.
18	Audit Log System	Centralized, tamper-proof audit of user and system events.
19	Notification History	Timeline view and search/filter of historical alerts.
20	Cloud & Hybrid Discovery	AWS, Azure, GCP connectors for hybrid asset discovery.
21	Compliance-as-a-Service	Scheduled compliance scans, reporting, and tenant SLA tracking.
22	Risk & Behavior Engine	UEBA-style anomaly detection with machine learning.
23	Smart Remediation	Automated playbooks for issue resolution and rollback.
🧮 Core Features by Category
1. Asset Discovery & Inventory

Automated discovery of servers, endpoints, and network devices

OS, role, and application fingerprinting

Cloud/hybrid connectors (AWS EC2, Azure VMs, GCP instances)

Agent-based and agentless modes

2. Security & Compliance

Continuous vulnerability and compliance scanning

Built-in frameworks: CIS Benchmarks, ISO 27001, NIST 800-53

Real-time compliance scoring

Data encryption and key rotation dashboards

3. Alerting & Incident Management

Configurable thresholds and rules

Branded HTML notifications (email/SMS/API)

Alert history, acknowledgment, and export

Integration hooks for SIEM and ticketing tools

4. Monitoring & Analytics

Metrics exported to Prometheus

Visualization in Grafana dashboards

Compliance trends and SLA metrics over time

5. User & Tenant Management

Multi-tenant structure with isolated schemas

Role-based dashboard views and permissions

Admin tools for tenant creation, feature enable/disable, and billing visibility

6. Data & Billing

Per-tenant cost tracking (scan count, storage use, features)

Automated invoice templates (CSV, PDF)

MSP dashboards for usage analytics

7. DevSecOps & Automation

GitHub Actions CI/CD pipelines

Dockerized deployment (tenantra_backend, tenantra_frontend, tenantra_db, tenantra_adminer)

Automated migration + seed scripts (run_migrate.sh, db_seed.py)

Validation suite & health checks via PowerShell and curl scripts

💡 Differentiators

True multi-tenant isolation with per-client encryption and audit trail.

Modular scanning engine covering system, network, identity, and compliance layers.

Self-contained DevOps stack deployable on-prem or cloud in minutes.

Compliance-as-a-Service model enabling MSPs to resell scanning and reporting.

Unified UI/UX combining dashboards, alerting, billing, and remediation.

📊 Example Workflow

Deploy Tenantra via Docker or cloud installer.

Register tenant(s) → auto-provision isolated schema.

Agents enroll and begin discovery scans.

Results appear in dashboards with compliance/risk scores.

Alerts trigger for violations or anomalies.

Admins export reports (CSV/PDF) or trigger remediation playbooks.

🧠 Built-in Intelligence

Machine-learning-ready telemetry pipelines.

Behavior analytics (UEBA) for anomaly detection.

Smart remediation recommendations linked to each compliance rule.

🌐 Deployment Options

On-Premises, Private Cloud, or Hybrid

Runs on Windows Server 2022, Linux (Ubuntu/Debian), or container platforms.

HTTPS enabled via self-signed or Let’s Encrypt certificates.

Integrates with FortiGate, TP-Link, and other firewalls for network discovery.

🔁 Data Lifecycle

All data encrypted at rest (AES-256).

Tenant retention and export policies (Phase 15).

Immutable logs retained per compliance framework.

🧭 End-User Experience

Responsive React dashboard with light/dark themes.

Role-aware navigation (Admin, User, Auditor).

One-click export, filters, and visual compliance charts.

Integrated health-check and status reporting per module.

In Summary

Tenantra is not just a monitoring tool—it's a full-stack DevSecOps and compliance automation platform.
It empowers IT teams and service providers to:

Discover assets automatically

Enforce security baselines

Monitor compliance continuously

Alert and remediate instantly

Manage tenants, users, and billing—all under one unified, secure, containerized system.


Tenantra Business Model Canvas
Section	Details
1. Value Proposition	• Unified platform for IT Discovery + Security + Compliance.
• Real-time visibility across on-prem, cloud, and hybrid environments.
• Multi-tenant SaaS with full data isolation.
• Compliance-as-a-Service (CaaS) with automated benchmarks (CIS, NIST, ISO 27001).
• Intelligent alerts + Smart Remediation.
• White-label ready for MSPs.
2. Customer Segments	• Enterprises with complex IT infrastructures.
• MSPs and MSSPs delivering managed security/compliance.
• Government & regulated entities.
• Mid-size businesses needing automated IT visibility.
• Cloud-native startups seeking DevSecOps automation.
3. Customer Relationships	• Subscription accounts per tenant.
• Dedicated customer success managers (for Enterprise/MSP).
• Automated onboarding wizard.
• Knowledge base + community portal.
• 24/7 support SLAs for premium plans.
4. Channels	• Direct SaaS web portal (tenantracloud.com).
• Resellers/MSP partners.
• Marketplace listings (Azure, AWS Marketplace).
• Email campaigns, webinars, security conferences.
• LinkedIn & YouTube educational content.
5. Revenue Streams	• Tiered subscription plans (Free / Basic / Pro / Enterprise).
• Add-on modules (Compliance, Threat Intel, Automation).
• Usage-based billing (scans, storage GB, tenants).
• Professional services & white-label licenses.
• Enterprise custom contracts.
6. Key Resources	• Tenantra Cloud platform (FastAPI + React).
• Scanning Module Engine & Agent framework.
• PostgreSQL + Prometheus stack.
• Security Vault (Key management).
• Development & DevOps teams.
• Brand & IP (Tenantra logo + domain).
7. Key Activities	• Platform development & module updates.
• Vulnerability & compliance database maintenance.
• Tenant provisioning & support.
• CI/CD operations & uptime monitoring.
• Partner enablement & training.
8. Key Partners	• Cloud providers (Azure, AWS, GCP).
• Cybersecurity vendors (Tenable, MISP feeds).
• Payment & billing providers (Stripe, Paddle).
• Resellers / MSPs.
• Training / certification partners (CompTIA, ITIL Academy).
9. Cost Structure	• Cloud hosting and infrastructure.
• Development & QA resources.
• Security audits & compliance costs.
• Customer support & SLAs.
• Sales & marketing.
• Partner commissions & licensing fees.
Key Strategic Highlights

Scalable SaaS model adaptable for on-prem or MSP resale.

Compliance differentiation — not just detection, but automation and reporting.

High recurring revenue potential through per-tenant and per-module pricing.

Strong entry barriers thanks to multi-tenant isolation, secure key management, and modular architecture.


Business Type: SaaS (Software-as-a-Service) Platform
Category:

IT Discovery, Security, and Compliance Automation

Core Business Model

Tenantra operates as a multi-tenant SaaS platform that organizations or MSPs (Managed Service Providers) can deploy on-premises, in private cloud, or as a hosted service.
It is designed to discover, secure, and monitor IT infrastructure across hybrid environments and provide compliance-as-a-service.

Business Classifications
Dimension	Classification
Industry	Information Technology / Cybersecurity / IT Infrastructure Management
Business Type	SaaS Platform (B2B, Multi-Tenant)
Primary Market	Enterprise IT, MSPs, and Mid-Size Organizations
Operating Model	Subscription-based (Monthly / Annual)
Deployment Model	Self-hosted, Managed SaaS, or Hybrid
Revenue Model	Tiered licensing per tenant, module, and storage usage
Delivery Type	Cloud-delivered platform accessible via web UI and API
Compliance Alignment	ISO 27001, NIST 800-53, ITIL v4, GDPR
Business Pillars

Discovery-as-a-Service
Automatic mapping of servers, endpoints, and networks for clients under a managed environment.

Compliance-as-a-Service (CaaS)
Continuous assessment of CIS, NIST, HIPAA, ISO 27001 benchmarks with scheduled reporting.

Security-as-a-Service
Vulnerability detection, key management, risk analytics, and alert automation.

Monitoring-as-a-Service
Integrations with Prometheus/Grafana for real-time visibility and SLA dashboards.

MSP & Enterprise Management
White-label-ready control panels for service providers to onboard and bill multiple clients.

Customer Segments

Enterprises needing full IT asset visibility, compliance automation, and reporting.

Managed Service Providers (MSPs) offering discovery/compliance as services.

Government & Regulated Entities requiring ISO/NIST/HIPAA alignment.

SMBs seeking affordable IT asset monitoring and baseline compliance.

Revenue Streams

Subscription Licenses – per tenant or organization.

Feature-based Tiers – Free, Basic, Pro, Enterprise.

Usage Billing – per scan, per storage volume, or per monitored endpoint.

Professional Services – setup, custom module development, integrations.

White-Label Licensing – for MSPs and OEM partners.

Example Positioning

Tenantra positions itself like “Qualys + Lansweeper + Tenable”, but re-imagined as a multi-tenant, compliance-centric SaaS that’s simple to deploy and affordable to scale.
It bridges the gap between IT asset management, security monitoring, and compliance automation — under one intelligent platform.

**Backend:**

*   **Framework:** FastAPI
*   **Database:** PostgreSQL (using SQLAlchemy and Alembic for migrations)
*   **Authentication:** JWT-based (using `python-jose` and `passlib`)
*   **Testing:** pytest

**Frontend:**

*   **Framework:** React
*   **Build Tool:** Vite
*   **Styling:** Tailwind CSS (with a Facebook-inspired theme)
*   **Routing:** React Router
*   **HTTP Requests:** Axios and Fetch
*   **Testing:** Playwright for end-to-end tests

## Building and Running

**Backend:**

*   Install dependencies: `pip install -r backend/requirements.txt`
*   Run the development server: `python backend/dev_server.py`

**Frontend:**

*   Install dependencies: `npm install`
*   Run the development server: `npm run dev`

**Full Stack (with Docker):**

*   Start the application stack: `make up`
*   Apply database migrations: `make migrate`
*   Seed the database: `make seed`

## Tenantra Development Conventions (v1.0)
1) Repository & Versioning

Monorepo with top-level folders: backend/, frontend/, infra/, scripts/, docs/, docker/, tests/, ops/.

Semantic Versioning: MAJOR.MINOR.PATCH (e.g., 2.3.7). Tag releases: vX.Y.Z.

Branching:

main: production-ready.

staging: pre-release integration.

dev: integration for daily work.

Feature branches: feat/<scope>-<short-desc>

Fix branches: fix/<scope>-<short-desc>

Conventional Commits (feat:, fix:, docs:, chore:, refactor:, perf:, test:, ci:). Enforce with commitlint.

Release Artifacts: Every packaged ZIP includes manifest.txt + checksums + RELEASE_NOTES.md.

2) Environments & Naming

Envs: dev, staging, prod.

Container & volume names must start with TENAT- (mandatory).

ENV var prefix: TENA_ (e.g., TENA_DB_URL, TENA_JWT_SECRET).

Docker images: tenantra/<service>:<semver>-<env> (e.g., tenantra/backend:1.4.2-prod).

Domains (as approved elsewhere): staging tenantra.homsi-co.com, production tenantra.be|app.

3) Security & Secrets

No hardcoded secrets. Load via .env files or secret stores (Vault/KeyVault).

Transport: HTTPS only; TLS 1.3; HSTS; strong ciphers.

At-rest: AES-256; per-tenant logical isolation.

JWT: HS256/RS256; 60min default; refresh policy; token blacklist hook-ready.

CORS: explicit allowlist (dev/staging/prod separately).

Rate limiting: enforce at API gateway + app level (login, scanning triggers).

Password policy: min length 12, complexity, breach check (HIBP-style), bcrypt.

Headers: CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy.

Dependency scanning: enabled in CI (e.g., pip-audit, npm audit, Docker Scout).

Keys rotation: 90 days; audit trails retained.

4) Backend (Python/FastAPI) Code Style

Python 3.11+. Black (line 100), isort, Flake8, mypy (strict-ish).

Architecture: app/ with api/ (routers), core/ (security/config), models/, schemas/ (Pydantic), services/, repositories/, workers/, telemetry/.

SQLAlchemy: models include id, created_at, updated_at, __repr__(), as_dict().

Alembic: single-head policy; migrations named YYYYMMDDHHMM_<scope>.py. CI fails on multiple heads.

API: RESTful paths (/v1/users, /v1/tenants), nouns, plural; idempotency where relevant.

Responses: Pydantic schemas; consistent envelope on errors.

Pagination: ?page= (1-based), ?page_size= (max 100), return total, items, page, page_size.

Errors: Standardized error codes structure {code, message, details?, trace_id}.

Auth: Authorization: Bearer <JWT>; /auth/me canonical for identity bootstrap.

Logging: JSON logs, trace_id on every request; rotation with size/time; PII-free.

Tracing/Metrics: OpenTelemetry exporters; Prometheus metrics on /metrics.

Background tasks: use celery/worker when long-running.

Validation: pydantic everywhere at edges (request/response/config).

5) Frontend (React/Vite) Code Style

TypeScript required. ESLint (airbnb+react), Prettier, Husky pre-commit.

State: React Query for server state, lightweight local state with Context/Zustand; no Redux unless needed.

Routing: react-router-dom. Enforce PrivateRoute & role gates.

UI: TailwindCSS + shadcn/ui; consistent design tokens; dark/light theme persisted.

API layer: single base via VITE_API_URL; re-exported client with interceptors (auth, errors).

Accessibility: WCAG AA, semantic HTML, keyboard navigation.

i18n: i18next, lazy-loaded namespaces.

Forms: react-hook-form + zod validation.

Build: env-specific builds (.env.development, .env.staging, .env.production).

Charts: Recharts; avoid excessive deps.

6) Data & Database Conventions

Schema: snake_case for tables/columns; plural table names (users, tenants).

FKs: <entity>_id with ON DELETE rules explicit.

Indexes: required for FK and high-selectivity columns.

PII fields: minimized, encrypted/hashed as appropriate.

Multi-tenancy: tenant_id required on tenant-scoped rows; server-side filters enforced (no client trust).

Migrations: forward-only; down revisions only for dev; data migrations separate from schema.

Seeds: idempotent; safe re-run; environment-aware.

7) Testing & Quality Gates

Test pyramid: unit > integration > e2e.

Coverage: backend ≥85%, frontend ≥80%; fails CI under thresholds.

e2e: Playwright/Cypress for auth & role flows.

Static Analysis: mypy, ESLint, flake8, bandit (security), trivy/scout (images).

Mandatory Validation: Redirect & Auth Lifecycle A1–E22 checked on every UI delivery (login, role gates, protected routes, logout, errors, no flicker).

Smoke checks after deploy: /health, /metrics, DB connectivity, 1 happy-path login.

8) CI/CD & Environments

GitHub Actions on self-hosted runner HO-Docker-22.

Pipelines:

Lint → Test → Build → Security scan → Package → Deploy (dev/staging/prod).

Block deploy if: tests fail, migration head conflict, CVE severity ≥ High (unless approved with waiver).

Docker: multi-stage builds; non-root user; pinned base image digests; SBOM export.

Compose/Stack: healthchecks on all services; containers/volumes named with TENAT- prefix.

Secrets: never in logs; injected via CI OIDC/vault; masked outputs.

Rollbacks: tagged images kept for N versions; DB backups pre-migrate.

9) Observability & Ops

Logs: JSON to stdout; aggregated via Loki/ELK; structured fields (service, env, trace_id, tenant_id, user_id).

Metrics: Prometheus; SLOs for API availability, p95 latency, worker queue depth.

Dashboards: Grafana folders per env; access via RBAC.

Alerts: Prometheus alert rules + email templates; on-call rotation documented.

10) Documentation & Governance

Docs tree: docs/ with README.md, DEPLOY.md, RUNBOOK.md, API.md, SECURITY.md, DATA_MODEL.md, RELEASE_CHECKLIST.md.

CHANGELOG: keep MASTER_CHANGELOG.md + “Impact Matrix” for cross-area effects.

ADRs: Architecture Decision Records under docs/adr/.

PR Template includes: scope, screenshots, tests added, A1–E22 validation checklist, migration note, risk/rollback.

Code Owners: enforce reviews for sensitive areas (auth, billing, migrations).

11) Error Handling & UX Guarantees

Never leak stack traces to users; show friendly messages with trace_id.

Global API error mapper on the frontend; toast + inline form feedback.

Retries: idempotent endpoints use safe retries with backoff; non-idempotent guarded.

Loading states: skeletons/spinners, no layout flicker on protected routes.

12) Performance & Limits

API: default page_size=25, max 100; server caps on payload (e.g., 5–10MB).

Caching: ETag/If-None-Match for GET lists; React Query caching tuned per endpoint.

N+1: prevent via eager loading or aggregate queries.

Background jobs: long ops offloaded to worker with job status endpoints.

13) Deliverables & Packaging

Every deliverable ZIP must include:

manifest.txt (full file list + sizes + hashes)

SETUP_GUIDE.md (non-technical A–Z steps)

VALIDATION_REPORT.md (tests run + A1–E22 results)

No empty or placeholder files.

Enforcement (Tooling)

Pre-commit hooks: Black, isort, Flake8, mypy, ESLint, Prettier.

Commitlint + lint-staged.

CI blockers: tests, coverage, security scans, alembic single-head check, TENAT- name checks.

Policy-as-code: simple repo policy script (ops/policy_check.py) to fail on violations.

## Tenantra Scanning Modules — Development Conventions (DB-first, no CSV at runtime)
A) Authority & Lifecycle

Authoritative Source: All modules live in the database. CSV files are allowed only as one-time import helpers in dev; they are never read at runtime.

Versioned Catalog: Each module has a stable UUID (module_id) and a semantic version in a separate module_versions row. Editing logic or parameters creates a new version, never mutating old versions.

States: draft → qa → released → deprecated → retired. Only released versions are schedulable.

Immutability: A module_version row is immutable once released. Fixes land in a new version.

Tenancy: Catalog is global; enablement is per-tenant via a join table (feature flags, plans).

B) Required Tables (conceptual contract)

modules — identity & metadata (UUID, slug, title, category, owner, created_at/updated_at).

module_versions — semantic version, checksum, parameter schema, exec profile, state, changelog, compatible OS/platforms.

module_parameters — optional param templates (name, type, defaults, required, validation rules) or embed inside module_versions.parameters_schema (JSONB).

module_runs — execution records (tenant_id, agent_id, version_id, status, timings, exit_code, resource usage).

module_results — normalized results (JSONB) with GIN indexes for common queries.

tenant_module_enablement — which tenants are allowed to use which module versions (and plan-based constraints).

DB-first rule: JSONB is used for flexible schemas (parameters_schema, result_body), but key fields must be indexed and validated in the app layer.

C) Naming & Identity

UUIDv4 keys: module_id, module_version_id, module_run_id.

Slug: Lowercase kebab-case unique per module (e.g., windows-autoruns).

Categories (controlled list): system_inventory, identity, network_exposure, filesystem, processes, registry, services_tasks, compliance, threat_intel, scheduling, cloud, ops_support.

OS/Platform tags: os: ["windows","linux","macos"], cloud: ["aws","azure","gcp"], requires_admin: true/false.

D) Parameter & Output Contracts

Parameters: Each module version carries a JSON Schema (parameters_schema) defining types, defaults, enums, min/max, regex.

Validate on create/update + at runtime before dispatch.

Reject unknown parameters (additionalProperties: false).

Output Envelope (module_results.result_body):

{
  "summary": { "passed": 12, "failed": 3, "score": 80 },
  "artifacts": [{ "type": "csv", "path": "/artifacts/…", "sha256": "…" }],
  "findings": [ { "id": "…", "severity": "low|med|high|critical", "resource": "…", "evidence": { } } ],
  "benchmarks": [{ "framework": "CIS", "control": "1.1.1", "status": "pass|fail" }]
}


No PII unless explicitly flagged; redact secrets.

Large payloads: store in object storage and reference via artifacts.

E) Execution Profile & Safety

Profiles: baseline_fast (≤30s), baseline_full (≤5m), deep_scan (≤20m).

Resource Limits: CPU/Memory/timeouts defined per version; enforced by the worker (kill on breach).

Idempotence: Repeated runs must not alter system state unless explicitly marked remediation.

Least Privilege: Declare requires_admin; scheduler/agent enforces elevation only when required.

Network Policy: Modules must declare outbound needs; default deny-all in agent sandbox.

F) Quality Gates (must pass to reach released)

Schema Lint: Parameters JSON Schema + Output contract validation with sample fixtures.

Static Security: No hardcoded secrets; signed artifact checksum; SBOM check (if applicable).

Unit Tests:

Parameter validation tests.

Parser correctness with golden files.

Edge cases (empty data, large data, permission error).

Integration Tests: Run on Windows + Linux agents (matrix) with synthetic targets.

Performance Tests: Ensure profile SLA (time/memory).

Determinism: Same input → same summarized output (ignoring timestamps/hostnames).

G) Seeding & Migrations (no CSV at runtime)

Initial Load: Modules are seeded via Alembic data migrations or a deterministic seed script that reads version-controlled fixtures from backend/fixtures/modules/*.yaml|json (not CSV).

Seed is idempotent (upsert by slug + version).

Fixture files are packaged inside the backend image.

Change Control:

Any new/changed module version → new Alembic data migration tagged with the catalog version (e.g., 20251104_add_windows_services_v1_2).

CI fails if the live DB catalog count or checksums differ from fixtures.

CSV Import (optional dev tool): A one-off CLI to parse your historic CSVs and write modules into DB, then commit the generated fixture JSON/YAML. The CSV is never referenced by the app.

H) CI/CD Enforcement

Catalog Check: A CI job runs catalog_check.py to compare:

Fixture set (in repo)

Alembic-seeded DB snapshot (ephemeral container)
→ Fails if mismatch (missing module/version, checksum drift).

No Multiple Alembic Heads: Pipeline blocks if >1 head.

Coverage: Module parsers/normalizers ≥85% coverage.

Policy Gate: The existing ops/policy_check.py extended to assert:

Presence of backend/fixtures/modules/

No *.csv reads in app code paths (simple grep rule)

TENAT- naming in any new compose.

I) RBAC & Multi-Tenant Rules

Visibility: Catalogue visible to admins; end-users see only released and enabled modules.

Enablement: tenant_module_enablement + plan matrix; scheduler refuses non-enabled modules.

Row-level Security (app layer): All module_runs/results filtered by tenant_id server-side (no client-supplied tenant trust).

J) Observability

Structured Logs: Every run emits {trace_id, module_slug, version, tenant_id, agent_id, status, duration_ms, error_code}.

Metrics:

Counters: module_runs_total{slug,version,status}

Histograms: module_run_duration_seconds{slug,version}

Gauges: agent_queue_depth

Audit Trail: Create/update/delete of module versions are audited with actor, diff, and reason.

K) Backward Compatibility & Deprecation

Compatibility window: Keep N previous released versions schedulable (configurable, e.g., N=2).

Deprecation flow: Mark deprecated with sunset date; UI warns; after date → retired (unschedulable) but results remain queryable.

L) Documentation Artifacts (per module/version)

README.md (purpose, pre-reqs, parameters, outputs, limits).

CHANGELOG.md (what changed vs previous).

SAMPLES/ (input/output samples for tests).

SECURITY.md (privilege needs, data sensitivity).

M) File & Path Conventions (in repo)
backend/
  fixtures/
    modules/
      catalog_v1/
        windows_autoruns@1.0.0.yaml
        windows_services@1.2.0.yaml
        linux_process_baseline@0.9.0.yaml
  app/
    modules/               # runners/normalizers (code)
      windows/
      linux/
      shared/
    services/module_catalog.py
    services/module_runner.py
    repositories/module_repo.py


Runners are pure Python with a stable interface; no inline shell unless sandboxed.

Normalizers must convert raw outputs → standard envelope.

##  end-to-end tests and how to run them.

NPM Scripts

Root package.json:1
e2e:init → npx playwright install --with-deps
e2e:smoke → playwright test --project=chromium --reporter=list
e2e:report → npx playwright show-report
frontend/package.json:1
test:e2e → playwright test
Configs

Playwright root config: playwright.config.ts:1
Playwright frontend config: frontend/playwright.config.ts:1
Playwright E2E Specs

Backend/API + app shell:
tests/e2e/system.spec.ts:1
tests/e2e/cors.spec.ts:1
Frontend UI E2E:
frontend/tests/e2e/process_monitoring.spec.ts:1
frontend/tests/e2e/integrity.spec.ts:1
Frontend UI flows and filters:
frontend/tests/moduleCatalog.spec.ts:1
frontend/tests/moduleCatalog.filters.spec.ts:1
Playwright Smoke Specs

tests/smoke/auth.spec.ts:1
tests/smoke/dashboard.spec.ts:1
tests/smoke/headers.spec.ts:1
tests/smoke/metrics.spec.ts:1
Test Utilities

Env helpers: tests/utils/testEnv.ts:1
Evidence writers (artifacts): tests/utils/evidence.ts:1
CI Workflows (E2E)

Playwright against staging: .github/workflows/e2e-staging.yml:1
UI smoke (Linux): .github/workflows/playwright-ui.yml:1
UI smoke (Windows): .github/workflows/playwright-ui-windows.yml:1
Newman E2E (Linux): .github/workflows/newman-e2e.yml:1
Newman E2E (Windows): .github/workflows/newman-e2e-windows.yml:1
Postman Collections (API E2E)

Collection: postman/tenantra_phases_1_7.postman_collection.json:1
Environment: postman/tenantra_local.postman_environment.json:1

## Development Conventions

*   **Styling:** The project uses Tailwind CSS for styling. A custom Facebook-inspired theme should be implemented with the same fonts style,colors , shadows and shoud be implemented for all bars (sidebar , top bar ,.... ).
*   **State Management:** The frontend uses a combination of `useState` and `useReducer` for state management.
*   **API Calls:** The frontend uses a combination of `axios` and `fetch` for making API calls. The goal is to standardize on `fetch`.
*   **Component Structure:** The frontend is structured into pages and reusable components. Complex components are broken down into smaller, more manageable components.
