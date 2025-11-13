```markdown
# Tenantra: Unified Project & Rollout Plan

This document provides the master reference for the Tenantra platform, combining the project summary, architecture, SaaS capabilities, and the complete multi-phase execution plan.

---

## 1. Project Summary

Tenantra is a secure, modular, multi-tenant platform designed for:

- IT discovery  
- Compliance  
- Risk detection  
- Alerting  
- Cost tracking  

It supports both internal IT teams and Managed Service Providers (MSPs).

The platform is built on a modular foundation, with over 120 scanning modules grouped into categories:

1. System Inventory  
2. Identity Management  
3. Network Exposure  
4. File System Auditing  
5. Services & Autoruns  
6. Kernel & Registry  
7. Threat Detection  
8. Anomaly Tracking  
9. Compliance Matching  
10. Alerting & Notifications  
11. Cost & Billing Metrics  
12. Orchestration Logic  

---

## 2. Architecture & Security

### 2.1 Architecture Overview

The platform is built on five key layers:

1. **Frontend (React + Tailwind)**  
   - Dashboards, alerts, compliance, billing, tenant panels  
   - Role-based visibility and navigation

2. **Backend (FastAPI)**  
   - REST APIs  
   - Scan controller & orchestration  
   - Agent manager  
   - Authentication & RBAC

3. **Agent (Python + PowerShell + Docker)**  
   - Runs scanning modules  
   - Supports Windows, Linux, macOS, and container variants

4. **Database (PostgreSQL + Redis)**  
   - Tenant data and module metadata  
   - Alerts, scan results, RBAC, cost and usage metrics  
   - Redis for caching / queues where needed

5. **DevSecOps (GitHub Actions)**  
   - Secure CI/CD pipelines for Dev/Staging/Prod  
   - Self-hosted runner on **HO-Docker-22**

### 2.2 Security Design

Security is enforced through several mechanisms:

| Feature          | Mechanism                                               |
|------------------|---------------------------------------------------------|
| Tenant Isolation | DB-level separation, `tenant_id` in all queries        |
| Auth             | JWT-based authentication + role-based access           |
| Secure Alerts    | No secrets in payloads; alerts signed / integrity-safe |
| WAF Ready        | Integration with FortiGate WAF layer                   |
| HTTPS Everywhere | Preconfigured self-signed certs (upgradable to public) |
| Rate Limiting    | FastAPI middleware / plugin                            |
| Secure Secrets   | `.env` files or encrypted GitHub secrets               |

---

## 3. Core SaaS & MSP Capabilities

The platform is designed as a fully monetizable, multi-tenant SaaS application.

### 3.1 Core SaaS Features

- **Multi-Tenant Architecture**: Each client fully isolated in data, scans, and roles.  
- **Tenant RBAC**: Roles such as `SUPER_ADMIN`, `ADMIN`, `MANAGER`, `READONLY`, and `BILLING_VIEWER`.  
- **Per-Tenant Module Activation**: Enable/disable specific scanning modules per tenant.  
- **Feature Tiering**: Free, Basic, Pro, Enterprise tiers.  
- **Usage Tracking & Cost Reporting**:  
  - Scan count  
  - Module volume  
  - Storage size per tenant  
  - CSV/PDF reporting  
- **Compliance Engine**: Mapping to frameworks (NIST, ISO, HIPAA, CIS).

### 3.2 MSP Readiness

- **Parent/Child Tenant Tree**  
  - MSPs can manage nested sub-tenants  
  - Scoped roles and permissions per tenant

- **Central Admin UI**  
  - Single control panel for all tenants  
  - Tenant switching, impersonation (with audit)

- **SLA Reporting**  
  - Risk, alerts, resolution metrics per tenant over time

### 3.3 Feature Matrix by Tier

| Feature                       | Free | Basic | Pro | Enterprise |
|-------------------------------|:----:|:-----:|:---:|:----------:|
| Agent-based Scanning          | ✅   | ✅    | ✅  | ✅         |
| Scan Scheduling               | ❌   | ✅    | ✅  | ✅         |
| Alerts (Email/In-App)         | ❌   | ✅    | ✅  | ✅         |
| Slack/Webhook Integration     | ❌   | ❌    | ✅  | ✅         |
| Dashboard Access              | ✅   | ✅    | ✅  | ✅         |
| Multi-Tenant Support          | ❌   | ❌    | ✅  | ✅         |
| Role-Based Access (RBAC)      | ❌   | ✅    | ✅  | ✅         |
| Module Control (per-tenant)   | ❌   | ✅    | ✅  | ✅         |
| Compliance Score              | ❌   | ✅    | ✅  | ✅         |
| PDF & CSV Export              | ❌   | ✅    | ✅  | ✅         |
| Audit Log Retention           | ❌   | ❌    | ✅  | ✅         |
| API Access                    | ❌   | ❌    | ✅  | ✅         |
| Billing Reports               | ❌   | ❌    | ✅  | ✅         |
| External Connectors           | ❌   | ❌    | ❌  | ✅         |
| AI Risk Detection             | ❌   | ❌    | ❌  | ✅         |

---

## 4. Environments & Deployment

The rollout strategy uses a three-environment flow:

| Environment  | URL / Location                  | Purpose                                                  |
|-------------|----------------------------------|----------------------------------------------------------|
| Development | Local or `/tenantra`             | Safe zone for feature building and internal testing      |
| Staging     | `tenantra.homsi-co.com`          | Internal UAT environment before release                  |
| Production  | `www.TenantraCloud.com`          | Public-facing environment for clients and admins         |

- All builds flow **Dev → Staging → Prod**, controlled by GitHub Actions.  
- Self-hosted CI/CD runner operates on **HO-Docker-22**.  

---

## 5. Detailed Rollout Plan (Phases 1–24)

This section outlines the detailed execution plan, merging sprint backlogs and the unified pipeline definition.

---

### Phase 1: Authentication & Session Management

**Goal:** Establish secure login and session handling.

- **Implement `/login` endpoint**  
  - Unauthenticated user can log in and receive a JWT session token.

- **Build `LoginPage` form (React)**  
  - Collects username/password and calls `/auth/login`.

- **Implement `/me` endpoint**  
  - Authenticated user can retrieve session, identity, and role.

- **Wire `AuthContext` (frontend)**  
  - Fetches user info on startup to initialize authentication state.

---

### Phase 2: Tenant Management & Agent Foundation

- **Create `Tenant` model (SQLAlchemy + Alembic)**  
  - Manages tenant configurations, plan, status.

- **Implement `GET /tenants`**  
  - Super admin can view all tenants with pagination.

- **Build `TenantListTable` (React)**  
  - UI to display tenant details.

- **Implement Agent Enrollment API**  
  - `POST /agent/enroll`: client admins register new agents.

- **Implement Heartbeat API**  
  - `POST /agent/heartbeat`: agents send “online” messages.

- **Implement Scan Dispatch API**  
  - `POST /scan/queue`: agents poll for new scan tasks.

- **Implement Scan Result API**  
  - `POST /scan/result`: agents submit scan execution outcomes.

- **Create Scan Result Migration**  
  - `scan_results` table for storing outcomes.

- **Implement CSV Export**  
  - `GET /scan/export/{tenant}`: export raw scan data for super admins.

---

### Phase 3: User Management, Roles, and Profile System

**Goal:** Extend authentication to full multi-role access control, user CRUD, and secure profile editing.

#### Batch 3.1: User CRUD API

- **Why:** Admins must manage user accounts with tenant isolation.  
- **How:**  
  - FastAPI endpoints `/users`, `/users/{id}` for GET, POST, PUT, DELETE.  
  - Extend `User` model with `email`, `is_active`, `role`, `tenant_id`.  
- **Output:** RESTful API for full user lifecycle management.

#### Batch 3.2: Role Enforcement & Access Control

- **Why:** Admin-only routes must be protected; UI filtered by role.  
- **How:**  
  - FastAPI dependency `Depends(get_current_user_with_role)`  
  - Add roles: `SUPER_ADMIN`, `ADMIN`, `USER`.  
- **Output:** Protected routes accessible only by allowed roles.

#### Batch 3.3: User Profile Update (Password & Email)

- **Why:** Users must manage their own profiles securely.  
- **How:**  
  - `GET` + `PUT` on `/users/me` for self-service updates.  
- **Output:** Secure interface for updating email / resetting password.

#### Batch 3.4: Admin UI – User Management Panel

- **Why:** Admins need a UI, not only raw APIs.  
- **How:**  
  - React route `/users` with table + modals for Add/Edit/Delete.  
- **Output:** Full frontend for managing users within a tenant.

#### Batch 3.5: Redirect & Auth Lifecycle Integration

- **Why:** Protected routes must be inaccessible to unauthorized users; sidebar must reflect role.  
- **How:**  
  - React `AuthContext` managing token and role  
  - `PrivateRoute` wrapper for protected routes  
- **Output:** Clean navigation and frontend security.

#### Batch 3.6: JWT Expiry & Session Handling

- **Why:** Auto logout after token expiry.  
- **How:**  
  - Add `exp` to JWT payload  
  - Frontend handles `401` to force logout  
- **Output:** Expired tokens automatically invalidate sessions.

#### Batch 3.7: User Activation/Deactivation

- **Why:** Admins must suspend users without deleting them.  
- **How:**  
  - `is_active` boolean on `User` model enforced during login  
  - Toggle in admin UI  
- **Output:** Deactivated users cannot log in.

#### Improvement (Batch 3.0.0)

- **Why:** Enhance security, traceability, and UI resilience.  
- **How:**  
  - Add `created_by`, `tenant_id`, `last_modified_by` to all DB models  
  - Use Pydantic for strict validation  
  - Middleware to log all changes  
  - Confirmation modals and retry logic in frontend  
- **Output:** Full traceability and more resilient flows.

---

### Phase 4: Alerting & Notification Rules

**Goal:** Implement alert pipeline, rule engine, and delivery mechanisms.

#### Batch 4.1: `AlertRule` Model + DB Schema

- **Why:** Rules define when and how alerts are triggered.  
- **How:**  
  - `AlertRule` model: `trigger_type`, `threshold`, `notification_type`, `tenant_id`, etc.  
- **Output:** DB schema for alert configuration.

#### Batch 4.2: Alert Dispatch Engine

- **Why:** Alerts must result in actions (email, webhook, etc.).  
- **How:**  
  - `alert_dispatcher.py` service connecting to SMTP and HTTP clients.  
- **Output:** Automatic triggering of alert actions when rules match.

#### Batch 4.3: Alert Rule Configuration Panel (Frontend)

- **Why:** Admins must define/manage rules via UI.  
- **How:**  
  - React route `/alerts` with forms for add/edit/delete rules.  
- **Output:** Per-tenant alert rule management.

#### Improvement (Batch 4.0.0)

- **Why:** Ensure tenant isolation, auditing, resilience.  
- **How:**  
  - Enforce `tenant_id` on all alert rule API endpoints  
  - Audit logging for rule changes  
- **Output:** Secure, traceable alert configuration system.

---

### Phase 5: Core Dashboard & Export Logic

**Goal:** Display compliance results, risk scoring, and provide export capabilities.

#### Batch 5.1: Compliance Result Viewer (UI)

- **Why:** Users must see scan results with compliance scoring.  
- **How:**  
  - React table at `/compliance` with columns: Module, Status, Risk, Last Scan.  
- **Output:** Pass/fail compliance view.

#### Batch 5.2: Compliance Export (CSV, PDF)

- **Why:** Reports needed for audits and clients.  
- **How:**  
  - Backend `/export/compliance` endpoint using pandas (CSV) and PDF generator (ReportLab/WeasyPrint).  
- **Output:** Branded PDF + downloadable CSV.

#### Batch 5.3: Compliance Score Trend Charts

- **Why:** Teams need posture trends over time.  
- **How:**  
  - Line chart (e.g., chart.js / ECharts) with daily compliance %  
- **Output:** Trend line of passing rate with date filters.

#### Improvement (Batch 5.0.0)

- **Why:** Tenant isolation and auditability.  
- **How:**  
  - Backend endpoints verify tenant from token scope  
  - Log all export actions to audit trail  
- **Output:** Tenant-aware dashboards and audited exports.

---

### Phase 6: Agent System, Scan Scheduling, and Execution

**Goal:** Automate and track scan scheduling and agent execution.

#### Batch 6.1: Agent Model & Enrollment API

- **Why:** Agents need identity and configuration.  
- **How:**  
  - `Agent` model  
  - `/agents/enroll` and `/agents/config/{id}` endpoints  
- **Output:** Agents enroll and fetch config (frequency, module sets).

#### Batch 6.2: Scheduled Scan Queue + Dispatcher

- **Why:** Automated periodic scans.  
- **How:**  
  - `ScheduledScan` table  
  - Celery + Redis for periodic queues  
- **Output:** Agents scan on defined schedules.

#### Batch 6.3: Result Upload API (JSON)

- **Why:** Central ingestion of scan data.  
- **How:**  
  - `/scan_result` API to accept structured JSON and store in `ScanResult` table  
- **Output:** Unified scan result ingestion.

#### Improvement (Batch 6.0.0)

- **Why:** Secure agent communication, better drift accuracy.  
- **How:**  
  - Pydantic validation for payloads  
  - Add `agent_signature`, `timestamp`, `tenant_id`, `scan_context_id`  
- **Output:** Structured, traceable scan orchestration.

---

### Phase 7: Module Engine & Compliance Mapping

**Goal:** Orchestrate scan jobs and map results to compliance rules.

#### Batch 7.1: Module Runner Logic (Python)

- **Why:** Modular, extensible scan engine.  
- **How:**  
  - `modules/` directory; each script returns standard JSON (`status`, `risks`, `messages`)  
- **Output:** Execute modules from queue with structured output.

#### Batch 7.2: Compliance Control Mapping & Scoring

- **Why:** Map scan results to compliance rules.  
- **How:**  
  - `ComplianceControl` and `ScanResultMapping` tables  
  - Assign weight and risk per control  
- **Output:** Risk scores and compliance coverage per scan.

#### Improvement (Batch 7.0.0)

- **Why:** Robust schemas and ingestion security.  
- **How:**  
  - Pydantic validation on module outputs  
  - Rate limiting and size checks on ingestion  
- **Output:** Malformed results rejected; efficient drift storage.

---

### Phase 8: File & Network Visibility

**Goal:** File system inventory and network exposure mapping.

#### Batch 8.1: File System Monitor (Agents)

- **Why:** Detect shadow apps, malware, EOL binaries.  
- **How:**  
  - Enumerate installed programs, DLLs, config files, with hashes  
- **Output:** File inventory with risk flags in compliance view.

#### Batch 8.2: Network Exposure Mapping

- **Why:** Open ports and exposed services = basic hygiene.  
- **How:**  
  - Netstat-like scanner: listening ports, bound IPs, firewall rules  
- **Output:** JSON of open ports with risk scoring, alert triggers.

#### Improvement (Batch 8.0.0)

- **Why:** Accurate, secure file/network data.  
- **How:**  
  - `agent_signature` + `tenant_id` in payloads  
  - Normalize file paths and process results for stable baselines  
- **Output:** Better baseline drift detection.

---

### Phase 9: Identity & Credential Exposure

**Goal:** Discover local accounts, group memberships, credential weaknesses.

#### Batch 9.1: Local User/Group Discovery

- **Why:** Stale accounts and misconfigured privileges are common attack paths.  
- **How:**  
  - Collect users, roles, last login, password expiry; compare to policy  
- **Output:** Local accounts list with policy violation alerts.

#### Batch 9.2: Hash Exposure Detection

- **Why:** Weak/reused/breached passwords must be flagged.  
- **How:**  
  - Detect hash types  
  - Optional check vs HaveIBeenPwned or local hash list  
- **Output:** Risk level based on reuse/weak hashes.

#### Improvement (Batch 9.0.0)

- **Why:** Secure handling of sensitive identity data.  
- **How:**  
  - Strict Pydantic validation  
  - Tenant verification on backend for each submission  
- **Output:** Secure ingestion of identity data.

---

### Phase 10: Process Inventory & Threat Indicators

**Goal:** Inventory running processes and detect suspicious behavior via drift.

#### Batch 10.1: Live Process Inventory

- **Why:** Detect unwanted software and anomalies.  
- **How:**  
  - Agent collects processes (name, PID, path, signed/unsigned)  
- **Output:** List of processes with risk levels.

#### Batch 10.2: Suspicious Behavior Detection (Baseline Drift)

- **Why:** Detect new/anomalous behavior.  
- **How:**  
  - Track drift between scans (processes, ports, files)  
- **Output:** Visual drift graph and alerts on major changes.

#### Improvement (Batch 10.0.0)

- **Why:** More accurate drift detection.  
- **How:**  
  - Hash-based diffing; store only changes  
  - Normalize process data  
- **Output:** Incremental, accurate drift data and alerts.

---

### Phase 11: Registry, Boot, and Autorun Integrity

**Goal:** Detect malicious registry entries, persistence, and boot tampering.

#### Batch 11.1: Registry Hive Audit (Windows)

- **Why:** Registry autoruns are common persistence locations.  
- **How:**  
  - Read key hives (e.g., `HKCU\Run`, `HKLM\Run`) and capture suspicious entries  
- **Output:** JSON of autorun entries with alerts.

#### Batch 11.2: Boot Configuration Verification

- **Why:** Detect manipulated boot/UEFI settings.  
- **How:**  
  - `bcdedit`, UEFI/GRUB checks vs baseline  
- **Output:** Bootloader status and secure boot flags.

#### Improvement (Batch 11.0.0)

- **Why:** Better precision and traceability.  
- **How:**  
  - Capture entries with timestamp, source, command lineage  
- **Output:** More contextual autorun alerts.

---

### Phase 12: Services and Task Scheduler Checks

**Goal:** Audit services and scheduled tasks for abuse.

#### Batch 12.1: Running Services & Daemons Audit

- **Why:** Attackers install malicious services for persistence.  
- **How:**  
  - Parse `systemctl` / `Get-Service` data, flag unknown/unsigned services  
- **Output:** Services list with risk flags.

#### Batch 12.2: Scheduled Execution & Cron Monitor

- **Why:** Scheduled scripts are a common persistence tactic.  
- **How:**  
  - Query `schtasks` on Windows, `/etc/crontab` and user crons on Linux  
- **Output:** Inventory of recurring jobs, with non-whitelisted scripts flagged.

#### Improvement (Batch 12.0.0)

- **Why:** Improve detection & reduce noise.  
- **How:**  
  - Normalize names; verify publishers / signatures  
- **Output:** More precise alerts, fewer false positives.

---

### Phase 13: Threat Intelligence (IOC + CVE)

**Goal:** Match scan results to external CVEs and threat intel feeds.

#### Batch 13.1: CVE Lookup by Software + OS Version

- **Why:** Compliance requires regular vulnerability checks.  
- **How:**  
  - Integrate NIST or local CVE feeds by software/OS version  
- **Output:** Matched CVEs per asset and exportable CVE report.

#### Batch 13.2: Threat IOC Matching Engine

- **Why:** Real-time detection of known threats.  
- **How:**  
  - Match IOCs (hashes/IPs/domains) against scan results  
- **Output:** Alert log for IOC matches.

#### Improvement (Batch 13.0.0)

- **Why:** Reduce false positives and noise.  
- **How:**  
  - De-duplicate CVEs by asset/software/scope/severity  
  - Rule-based filtering (e.g., suppress if patch known)  
- **Output:** Actionable CVE/IOC alerts.

---

### Phase 14: Compliance Engine Expansion

**Goal:** New compliance frameworks and control-based reporting.

#### Batch 14.1: Framework Template Builder

- **Why:** Industry-specific mappings (healthcare, finance, etc.).  
- **How:**  
  - Upload/import JSON templates for frameworks  
  - UI to assign modules to controls  
- **Output:** Framework library (ISO, HIPAA, NIST, etc.).

#### Batch 14.2: Control-Based Reporting & Coverage Map

- **Why:** Show pass/fail per control for stakeholders.  
- **How:**  
  - Map scan data to controls; show % coverage per scan  
- **Output:** Tenant dashboard with audit status and exportable summary.

#### Improvement (Batch 14.0.0)

- **Why:** Traceability to evidence.  
- **How:**  
  - `ControlMap` table linking scans to framework rules  
  - Drill-down from control → failing scan evidence  
- **Output:** Framework-level audit trail.

---

### Phase 15: Data Retention, Archiving, and Export Tools

**Goal:** Implement data retention policies and full export.

#### Batch 15.1: Retention Policies & Cleanup Jobs

- **Why:** Control disk usage and meet GDPR/ISO limits.  
- **How:**  
  - `RetentionPolicy` table  
  - Celery job cleaning old scan results/logs  
- **Output:** Regular deletion of expired data.

#### Batch 15.2: Full Data Export System (ZIP + JSON)

- **Why:** Tenants need offline compliance snapshots.  
- **How:**  
  - `/export/full` creates structured ZIP with all tenant data  
- **Output:** Full (optionally password-protected) ZIP export.

#### Improvement (Batch 15.0.0)

- **Why:** Transparent, safe retention.  
- **How:**  
  - Retention “dry-run” mode + daily summary logs  
  - Policy preview before deletion  
- **Output:** Configurable, auditable retention.

---

### Phase 16: MSP Admin Control & Delegation

**Goal:** Central MSP dashboard for tenants and billing.

#### Batch 16.1: MSP Super Admin Dashboard

- **Why:** Efficient tenant switching and oversight.  
- **How:**  
  - Route `/msp/clients` with tenant list  
  - Impersonation of tenant dashboards (with audit)  
- **Output:** Central MSP dashboard (role: `MSP_ADMIN`).

#### Batch 16.2: MSP Usage & Cost Dashboard

- **Why:** Transparent billing for scan volume and storage.  
- **How:**  
  - Usage table tracking monthly scans, agents, retention size, CSV/API export  
- **Output:** Per-tenant usage and cost report.

#### Improvement (Batch 16.0.0)

- **Why:** Secure isolation and billing accuracy.  
- **How:**  
  - `msp_scope_token` for MSP access trails  
  - Cross-check usage stats vs raw scan logs  
- **Output:** Verifiable billing and scoped MSP access.

---

### Phase 17: Scan Orchestration & Feedback Engine

**Goal:** Parallelize scans and expose agent feedback.

#### Batch 17.1: Multi-Agent Scan Trigger System

- **Why:** Trigger sweeps across all agents.  
- **How:**  
  - `/scan/trigger` API with agent selector; queue N jobs via Celery  
- **Output:** Distributed scanning with real-time status.

#### Batch 17.2: Result Feedback / Agent Status Updates

- **Why:** Provide execution logs/error context.  
- **How:**  
  - `ScanResult` fields: `execution_log`, `status_code`  
- **Output:** Human-readable feedback in UI.

#### Improvement (Batch 17.0.0)

- **Why:** Stronger incident triage.  
- **How:**  
  - Log severity levels for failures/retries/failed uploads  
- **Output:** Detailed feedback and notification metadata.

---

### Phase 18: Audit Log System

**Goal:** Full audit trail for admin actions (ISO/HIPAA/SOC2).

#### Batch 18.1: Action Logging for Admin Events

- **Why:** Trail of configuration, user, and policy changes.  
- **How:**  
  - `AuditLog` model (`actor_id`, timestamp, `action_type`, etc.)  
  - Middleware on sensitive routes  
- **Output:** Viewable history of admin actions.

#### Batch 18.2: UI Panel for Audit Logs

- **Why:** Compliance officers need review access.  
- **How:**  
  - React table at `/audit-logs` with filters (time, user, action)  
- **Output:** Exportable CSV of history, restricted to `SUPER_ADMIN`.

#### Improvement (Batch 18.0.0)

- **Why:** Ensure logs are part of lifecycle.  
- **How:**  
  - Include audit logs in retention/export policies  
  - Clearly link to tenant/user IDs  
- **Output:** Comprehensive, secure audit trail.

---

### Phase 19: Alert History and Notification Viewer

**Goal:** Show which alerts were sent, failed, or acknowledged.

#### Batch 19.1: Notification Log Table

- **Why:** Prevent alert fatigue and track failures.  
- **How:**  
  - `NotificationLog` table (`timestamp`, `rule_id`, `channel`, `status`, etc.)  
- **Output:** Historical notifications with delivery status.

#### Batch 19.2: Notification Viewer (Frontend)

- **Why:** Visual traceability of notifications.  
- **How:**  
  - Read-only panel at `/notifications/history`  
- **Output:** Visual list of notifications with status badges.

#### Improvement (Batch 19.0.0)

- **Why:** Full audit and re-test capability.  
- **How:**  
  - Extend `NotificationLog` with `retry_count`, `webhook_status`, `message_id`  
- **Output:** Ability to replay/re-test alerts.

---

### Phase 20: Cloud & Hybrid Asset Discovery

**Goal:** Inventory assets across AWS, Azure, GCP for hybrid visibility.

#### Batch 20.1: Cloud Provider Integration

- **Why:** Full visibility in enterprise/cloud environments.  
- **How:**  
  - Integrate AWS (boto3), Azure, GCP SDKs  
  - Pull VMs, buckets, DBs, identity groups  
- **Output:** Cloud asset table by type/provider.

#### Batch 20.2: Hybrid Dashboard View

- **Why:** Unified view of on-prem + cloud.  
- **How:**  
  - `/inventory` dashboard merging agent and cloud assets  
- **Output:** Unified IT asset view per tenant.

#### Improvement (Batch 20.0.0)

- **Why:** Handle throttling/inconsistent cloud API data.  
- **How:**  
  - Rate-limit awareness and asset verification routines  
- **Output:** Accurate, reliable hybrid asset inventory.

---

### Phase 21: Compliance-as-a-Service (CaaS)

**Goal:** Automated, branded compliance reports via email.

#### Batch 21.1: Automated Monthly Compliance Emails

- **Why:** MSP/SMB clients want emailed summaries.  
- **How:**  
  - Scheduled Celery task generating PDFs monthly, emailing tenant admins  
- **Output:** Auto-sent compliance snapshots (PDF).

#### Batch 21.2: Report Branding and Multi-Framework Support

- **Why:** White-label and multi-framework reporting.  
- **How:**  
  - PDF template engine with logos, tenant info, frameworks  
- **Output:** Personalized, audit-ready reports.

#### Improvement (Batch 21.0.0)

- **Why:** Prevent silent failures and misaddressed reports.  
- **How:**  
  - Delivery receipts, per-tenant overrides for schedules/recipients  
- **Output:** Trusted, timely monthly emails.

---

### Phase 22: Risk Scoring & Behavior Drift Engine

**Goal:** Aggregate risk scores and track anomalous behavior.

#### Batch 22.1: Real-Time Risk Score Aggregator

- **Why:** Simple 0–100 scores for exposure.  
- **How:**  
  - Weight scores per module/control  
  - Roll up to asset, tenant, global views  
  - Dashboard scorecard widget  
- **Output:** Tenant risk score with colored indicators and trends.

#### Batch 22.2: Anomaly Detection & Drift Tracking

- **Why:** Early warning for behavior changes.  
- **How:**  
  - Baseline history of processes, ports, hashes  
  - Alerts for new/rare activity  
- **Output:** Drift alerts on dashboard / via webhooks.

#### Improvement (Batch 22.0.0)

- **Why:** Make scoring explainable and useful.  
- **How:**  
  - Tenant-defined score weights  
  - Drift baseline across time and assets (not just last scan)  
- **Output:** Explainable, tenant-tuned scores and intelligent drift detection.

---

### Phase 23: Smart Fixes and Remediation Toolkit

**Goal:** Provide actionable fix suggestions and optional automation.

#### Batch 23.1: Fix Suggestion Engine

- **Why:** Users need clear, actionable fixes.  
- **How:**  
  - Map each module’s failure to fix text (e.g. “Open port 23” → “Block via firewall”)  
- **Output:** Fix guidance per compliance failure.

#### Batch 23.2: Automated Fix Scripts (Optional)

- **Why:** MSPs/power users want one-click remediation.  
- **How:**  
  - Opt-in scripts executed by agents when allowed  
- **Output:** Remote fixes with corresponding audit log entries.

#### Improvement (Batch 23.0.0)

- **Why:** Avoid breaking systems with aggressive fixes.  
- **How:**  
  - “Preview-only” mode + rollback option  
  - Label each fix with compliance control impact  
- **Output:** Safe, controlled, and traceable remediation.

---

### Phase 24: Self-Service Tenant Provisioning + SSO

**Goal:** Allow new tenants to onboard themselves securely.

**Tasks:**

- Build signup flow (invite code or approval-based).  
- Implement SSO support (Microsoft, Google, SAML).  
- Auto-provision default modules based on subscription tier or template.

---

## 6. Project Reference & Infrastructure

### 6.1 Integrated Components

- **HO-WEB-22**:  
  - Hosts Tenantra frontend and public site (Staging only).  

- **HO-MAIL-22**:  
  - Mail server for alerts (MailEnable, Staging only).  

- **HO-JIRA-22**:  
  - Target for future ticketing/automation integration.  

- **HO-DOCKER-22**:  
  - Runs GitHub runner and backend agent containers.  

- **HO-SQL-19**:  
  - Optional analytics and storage expansion.

### 6.2 Reference URLs

| Purpose          | URL / Hostname                             |
|------------------|--------------------------------------------|
| Production       | `www.TenantraCloud.com` (TBD deployment)   |
| Staging          | `Tenantra.homsi-co.com`                    |
| GitHub Actions   | `git.homsi-co.com` (private runner)        |
| Email Alerts     | `mail.homsi-co.com`                        |
| Docker Host      | `HO-Docker-22.HOMSI.local` (`10.0.0.33`)  |
```
