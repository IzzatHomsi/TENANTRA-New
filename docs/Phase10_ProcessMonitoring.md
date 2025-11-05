# Phase 10 – Process Monitoring & Drift Detection

This phase introduces end-to-end visibility into runtime processes with drift detection, baseline management, and UI coverage.

## Backend
- Added ORM models: `ProcessSnapshot`, `ProcessBaseline`, `ProcessDriftEvent` with Alembic revision `T_003_phase10_process_tables`.
- New FastAPI router (`/processes`) exposes:
  - `POST /processes/report` – agents upload full process inventories, drift is recorded, compliance and integrity events are emitted automatically.
  - `GET /processes?agent_id=…` – fetch the latest snapshot for an agent.
  - `GET /processes/drift` – review historical drift events.
  - `GET|POST /processes/baseline` – manage agent or tenant-level baselines.
- Drift events spawn `IntegrityEvent` rows and update the `process_integrity` compliance module (pass/fail).

## Agent collectors
- `tools/Phase10_ProcessMonitor.ps1` gathers Windows processes (owner, hash, command line) and posts to the API.
- `tools/phase10_process_monitor.sh` provides the Linux equivalent using `/proc` and Python for hashing.
- Both scripts accept `TENANTRA_AGENT_ID`, `TENANTRA_API_BASE`, `TENANTRA_API_TOKEN`, and optional `TENANTRA_TENANT_ID` environment variables.

## Frontend
- New page `ProcessMonitoring` (route `/process-monitoring`) exposes:
  - Live process table for an agent with quick baseline seeding.
  - Drift event timeline and summary chips.
  - Editable baseline grid with critical toggles and hash/user expectations.
- Navigation updated with a “Runtime Integrity” section linking to Process Monitoring, Persistence, and Threat Intelligence.

## Tests
- `backend/tests/test_process_monitoring.py` exercises baseline persistence and verifies drift detection for missing critical processes.

## Validation tips
1. Apply a baseline for an agent via UI or API.
2. Submit a matching `POST /processes/report` payload – expect `drift.events` empty and a `pass` compliance row.
3. Submit a payload omitting a critical process – observe a `missing_critical` drift event, `IntegrityEvent` entry, and compliance `fail` result.
