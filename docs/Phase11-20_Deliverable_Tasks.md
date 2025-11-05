# Phases 11→20 Deliverable Task Breakdown

> Continuation of the Tenantra platform roadmap, extending the Phase 10 deliverable format to outline implementation scope for Phases 11 through 20.

## Phase 11 – Registry & Boot Integrity

**Why It’s Needed**
- Malware persistence commonly hides in Windows registry keys and boot records across Windows/Linux/UEFI.
- Attackers leverage autoruns, run keys, and bootloader configuration to survive reboots.

**How To Implement**
- **Backend:** Add models `registry_snapshot`, `boot_config`, and `integrity_event`.
- **Agent:**
  - Windows: Export critical registry hives and autorun entries.
  - Linux: Collect bootloader configurations (`/boot/grub/grub.cfg`, init scripts).
- **Frontend:** Provide a registry/boot integrity dashboard with diff viewing.

**What It Delivers**
- Detection of hidden persistence mechanisms.
- Compliance evidence for CIS/ISO controls.

**Dependencies / Risks**
- Depends on the agent scheduling capabilities delivered in Phase 6.
- Registry dumps may contain sensitive values; ensure transport and database encryption.

**Task Deliverables**
- Models and migrations.
- Agent registry and boot collectors.
- Drift analysis in the backend.
- Dashboard visualization with alerts.

## Phase 12 – Services & Task Scheduler

**Why It’s Needed**
- Attackers abuse Windows Services and Scheduled Tasks for persistence.
- Non-standard cron jobs or unexpected services indicate potential compromise.

**How To Implement**
- **Backend:** Add `services_snapshot` and `tasks_snapshot` models.
- **Agent:**
  - Windows: Collect `Get-Service` and `Get-ScheduledTask` output.
  - Linux: Enumerate systemd services and cron jobs.
- **Frontend:** Services and tasks table with baseline versus drift views.

**What It Delivers**
- Visibility into persistence vectors.
- Compliance mapping, including checks for disabled AV/firewall services.

**Dependencies / Risks**
- Requires baseline management introduced in Phase 10.
- Large cron dumps could impact performance; optimize the diff engine.

**Task Deliverables**
- Models for services and scheduled tasks.
- Agent collectors.
- Diff and drift detection.
- Dashboard integration.

## Phase 13 – Threat Intelligence

**Why It’s Needed**
- Local discovery benefits from enrichment that links processes, IPs, and hashes to known bad indicators.
- Enables proactive defense via IOCs and threat intelligence feeds.

**How To Implement**
- **Backend:** Integrate with open threat intelligence feeds (MISP, AlienVault OTX, AbuseIPDB).
- **Database:** Introduce `ioc_feed` and `ioc_hit` models.
- **Frontend:** Threat intelligence dashboard highlighting flagged assets and processes.

**What It Delivers**
- Contextual risk detection when hashes or IPs match threat intelligence.
- Added value for MSSP partners.

**Dependencies / Risks**
- Threat intelligence APIs may require API keys or entail licensing costs.
- Feeds need a secure update mechanism.

**Task Deliverables**
- Threat intelligence integration services.
- IOC ingestion and matching engine.
- Frontend risk intelligence panel.
- Alerting for high-priority TI hits.

## Phase 14 – Compliance Control Expansion

**Why It’s Needed**
- Customers expect comprehensive compliance coverage beyond ISO/NIST (HIPAA, PCI, GDPR, CIS).

**How To Implement**
- **Backend:** Expand the compliance rules table with multi-framework mappings.
- **Frontend:** Deliver a compliance matrix UI that shows control coverage.
- **Export:** Support framework-specific PDF/CSV reports.

**What It Delivers**
- Multi-framework compliance support.
- Differentiation versus competing platforms.

**Dependencies / Risks**
- Builds on the compliance dashboard from Phase 5.
- Mapping overhead requires manageable, CSV-driven maintenance.

**Task Deliverables**
- Expanded compliance rules.
- Compliance mapping engine.
- Multi-framework exports.
- Compliance UI matrix.

## Phase 15 – Retention & Data Export

**Why It’s Needed**
- Clients require configurable data retention windows (90/180/365 days).
- Audits and regulators need exportable datasets.

**How To Implement**
- **Backend:** Define data retention policies per tenant.
- **Storage:** Use partitioned tables or S3-like archiving for aged data.
- **Frontend:** Tenant settings UI for retention policy selection.
- **Exports:** Provide CSV, JSON, PDF, and ZIP export formats.

**What It Delivers**
- Regulatory compliance for data retention requirements.
- Self-service data exports for clients.

**Dependencies / Risks**
- Storage cost scaling must be monitored.
- Requires integration with backup and export systems.

**Task Deliverables**
- Retention settings per tenant.
- Export API.
- Dashboard export UI.
- Automated purge jobs.

## Phase 16 – MSP Control & Billing

**Why It’s Needed**
- Managed service providers need multi-tenant control and billing automation.
- Enables monetization and upsell opportunities for Tenantra.

**How To Implement**
- **Backend:** Add `usage_log`, `billing_plan`, and `invoice` models.
- **Frontend:** Admin MSP panel for usage visibility and billing administration.
- **Exports:** Generate PDF invoices.

**What It Delivers**
- Automated cost tracking.
- Transparency for clients regarding billing.

**Dependencies / Risks**
- Relies on Phase 15 retention and usage metrics.
- Invoice logic must support multi-currency and tax calculations.

**Task Deliverables**
- Usage and billing models.
- MSP control panel.
- Invoice export.
- Tenant billing reports.

## Phase 17 – Scan Orchestration

**Why It’s Needed**
- Coordinated scanning is necessary across many tenants and hosts.
- Administrators must schedule, stagger, and prioritize scans effectively.

**How To Implement**
- **Backend:** Implement an orchestration service backed by a queue.
- **Database:** Add `scan_job` and `scan_result` models.
- **Frontend:** Provide scan scheduler and monitoring UI.

**What It Delivers**
- Centralized scan control.
- Reduced resource conflicts during scan execution.

**Dependencies / Risks**
- Requires the stable scheduling engine from Phase 6.
- Orchestration must scale horizontally.

**Task Deliverables**
- Orchestration service.
- Scan job models.
- Scheduling UI.
- Scan status tracker.

## Phase 18 – Audit Log System

**Why It’s Needed**
- Audit logs underpin compliance and insider threat detection.
- Mandated by ISO, NIST, and SOC 2 frameworks.

**How To Implement**
- **Backend:** Introduce structured logging with an `audit_log` model.
- **Frontend:** Admin log viewer with filtering and search.
- **Export:** Provide CSV and PDF export options.

**What It Delivers**
- End-to-end traceability of actions.
- Meets auditor expectations.

**Dependencies / Risks**
- Log volume can grow quickly; implement compression and rotation.
- Works alongside Phase 15 retention for lifecycle management.

**Task Deliverables**
- Audit log models.
- Log viewer UI.
- Export functionality.
- Alerts for suspicious actions.

## Phase 19 – Notification History

**Why It’s Needed**
- Tenants need a historical record of alerts and notifications.
- Compliance requires tracking who received which notifications and when.

**How To Implement**
- **Backend:** Add a `notification_log` table.
- **Frontend:** Build a notification history dashboard with filtering and search.
- **Export:** Support per-tenant PDF and CSV exports.

**What It Delivers**
- Transparency into alerting history.
- Strengthens client trust.

**Dependencies / Risks**
- Depends on the notification engine established in Phase 4.

**Task Deliverables**
- Notification log model.
- Dashboard history viewer.
- Export UI.
- Integration with alerting flows.

## Phase 20 – Cloud & Hybrid Discovery

**Why It’s Needed**
- Many customers operate hybrid environments across on-premises and Azure/AWS/GCP.
- Requires connectors for comprehensive cloud asset discovery.

**How To Implement**
- **Backend:** Implement cloud connectors for Azure AD, AWS APIs, and GCP APIs.
- **Agent:** Collect local cloud CLI configurations (`aws`, `az`, `gcloud`).
- **Frontend:** Provide a cloud assets dashboard segmented by tenant and cloud provider.

**What It Delivers**
- Unified visibility across on-premises, cloud, and hybrid assets.
- Key differentiator compared with Lansweeper and Axonius.

**Dependencies / Risks**
- API throttling and usage costs must be managed.
- Requires secure credential storage (e.g., Vault).

**Task Deliverables**
- Cloud connectors.
- Multi-cloud discovery engine.
- Dashboard hybrid view.
- Cloud tenant mapping.

