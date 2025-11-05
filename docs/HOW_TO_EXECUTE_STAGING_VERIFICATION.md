# How to Execute — Live Staging Verification

## Option A — GitHub Actions (Recommended)
1. Add repo secrets:
   - `E2E_ADMIN_USER`, `E2E_ADMIN_PASS`
   - `E2E_STD_USER`, `E2E_STD_PASS`
2. Run workflow `.github/workflows/e2e.yml`.
3. Download artifacts:
   - `playwright-report/`
   - `evidence/`
   - `evidence-curl/`

## Option B — Local (Developer)
### Linux/Mac
```bash
export E2E_BASE_URL="https://Tenantra.homsi-co.com"
export E2E_ADMIN_USER="admin_sandbox@your-domain"
export E2E_ADMIN_PASS="********"
npm ci
npx playwright install --with-deps
npx playwright test --project=chromium --reporter=list
bash scripts/evidence/curl_smoke.sh
```

### Windows PowerShell
```powershell
$env:E2E_BASE_URL="https://Tenantra.homsi-co.com"
$env:E2E_ADMIN_USER="admin_sandbox@your-domain"
$env:E2E_ADMIN_PASS="********"
npm ci
npx playwright install --with-deps
npx playwright test --project=chromium --reporter=list
.\scripts\evidence\curl_smoke.ps1
```

## Acceptance Checks
- `/health` -> 200/204
- `/openapi.json` -> 200/401/403
- Login -> redirect to /dashboard or /home
- `/scans` shows table or Completed
- HSTS/CSP headers present
- `/metrics` returns Prometheus text
