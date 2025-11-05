# MASTER_CHANGELOG
CI/CD: enforce staging overrides in deploy script; add manual trigger; normalize remote URL (lowercase).

Release: Phase 11 hardening (backend, observability, CI/CD, frontend auth)

Highlights
- Backend tests made deterministic and green (pytest server fixture, SQLite bootstrap)
- Security: headers (HSTS/CSP/COOP/COEP), rate-limit env read, subprocess hygiene, SQL allowlist
- Observability: Prometheus rules + alerts; Grafana dashboards (RED view + latency quantiles)
- CI/CD: Self-hosted staging deploy workflow + post-deploy probes; htpasswd provisioning for Grafana
- Frontend: Auth lifecycle polish (token consistency, redirect restore, global notices, error banners)

Changes (summary)
- Backend
  - Start dev API in pytest via `backend/tests/conftest.py`; auto SQLite and bootstrap
  - Integrity registry removal severity fix (baseline lookup)
  - Port scan exception narrowing; worker health bind localhost by default
  - Scripts: subprocess via `shutil.which`, SQL cleanup allowlist, Bandit annotations
- Observability
  - Prometheus `rule_files`, RED/USE alert rules, latency quantile recording rules
  - Grafana provisioning: dashboards, contact points, policies; serve at `/grafana` via Nginx
- CI/CD
  - `.github/workflows/deploy-staging.yml` and `post-deploy-probes.yml`
  - `.env.staging.example` (strict CSP/HSTS/CORS)
- Frontend
  - Global notice banner + 401/403 handling; error banner; token key standardization; login redirect restore

Validation
- Backend: `PYTHONPATH=backend python -m pytest -q backend/tests` ΓåÆ green
- Dev smoke: `pwsh tools/smoke.ps1 -BaseUrl http://localhost` ΓåÆ SMOKE OK
- Prometheus: target up; rules loaded; Grafana overview visible


### CI/CD: Staging Git sync + auto-deploy via self-hosted runner (HO-DOCKER-22)
- Fixed dirty tree and divergence on staging host by stashing and hard-resetting to origin/main; normalized git config (longpaths=true, autocrlf=false, pull.ff=only).
- Added workflow .github/workflows/staging-deploy.yml (push on main) running on self-hosted Windows; invokes ops/pull_and_redeploy.ps1.
- Script performs compose down -v, up --build -d, waits for DB, runs Alembic migrations, captures artifacts and health checks.
- Evidence: Staging_GitSync_FixLog.txt, artifacts/*, Staging_Sync_Report.md.