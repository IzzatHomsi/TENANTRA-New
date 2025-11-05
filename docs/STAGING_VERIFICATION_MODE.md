# Tenantra — Staging Verification Mode (Quick Guide)

## Preconditions
- Staging URL: https://Tenantra.homsi-co.com
- Sandbox tenant with Admin and Standard user creds (provided via CI secrets).
- App exposes: /health, /openapi.json, /auth/login, /auth/me, /metrics.

## What runs in CI
- `ci-python.yml`: ruff, mypy, bandit, pytest (smoke)
- `e2e.yml`: Playwright smoke against staging; uploads HTML report

## Manual checks (browser)
1. Login as Admin → reach dashboard/home.
2. Navigate to Scans → trigger one representative scan.
3. Confirm Completed/result table appears.
4. Verify headers (CSP, HSTS) via DevTools network.
5. Confirm HTTPS redirect from http:// to https://.

## Evidence bundle
- CI artifacts: Playwright HTML report
- Logs: GitHub Actions logs for both jobs
- Optional: save screenshots and traces for failed tests
