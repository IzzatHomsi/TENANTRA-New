# Tenantra — Option B Cleanup (External CI)

You selected **Option B**: keep CI/E2E outside this repo. This package removes the small set of files I added in Batch 2 (Playwright, CI workflow, env sample, hooks).

## Files this script will remove (if present)
- `playwright.config.ts`
- `tests/utils/testEnv.ts`
- `tests/smoke/auth.spec.ts`
- `tests/smoke/dashboard.spec.ts`
- `tests/smoke/scans.spec.ts`
- `.github/workflows/e2e.yml`
- `env/.env.development.sample`
- `tools/githooks/pre-commit.ps1`
- `tools/compose_validate.ps1`

> Note: If `package.json` was originally in your repo, it is **not** removed by this script. If you want it removed, do so manually.

## How to run
From the **repo root** in PowerShell:

```powershell
# Dry run (see what would be removed)
.\cleanup_batch2_additions.ps1 -WhatIf

# Execute removal
.\cleanup_batch2_additions.ps1
```

## After cleanup
- Your repository will no longer contain Playwright/CI artifacts added in Batch 2.
- CI/E2E remains fully **external** (your existing pipelines).

If you later want me to wire a **read-only staging verification job** that only pulls artifacts (without altering your repo), we can do that in a separate batch.
