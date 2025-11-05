# Live Staging Verification Mode — Execution Guide

## Environment
- Base URL: https://Tenantra.homsi-co.com
- Provide secrets: E2E_ADMIN_USER, E2E_ADMIN_PASS, E2E_STD_USER, E2E_STD_PASS

## What to run
### A) GitHub Actions
- Workflow: `.github/workflows/e2e.yml`
- Artifacts uploaded:
  - `playwright-report/` (HTML)
  - `evidence/` (headers.json, homepage html summary, metrics.txt)
  - `evidence-curl/` (headers/body from curl)

### B) Manual (local)
```bash
export E2E_BASE_URL="https://Tenantra.homsi-co.com"
export E2E_ADMIN_USER="admin@..."
export E2E_ADMIN_PASS="***"
npm ci
npx playwright install --with-deps
npx playwright test --project=chromium --reporter=list
bash scripts/evidence/curl_smoke.sh
```

## Acceptance
- /health -> 200/204
- /openapi.json -> 200/401/403 acceptable
- UI login -> redirects to /dashboard or /home
- /scans -> table visible or "Completed"
- Headers include HSTS/CSP (review `evidence/http_headers.json`)
- /metrics returns text with counters/gauges
