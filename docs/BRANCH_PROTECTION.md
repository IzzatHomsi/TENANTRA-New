Branch Protection and Required Checks
====================================

This guide walks you through enabling branch protection on `main` and requiring CI checks for Tenantra.

Recommended required checks

- Tenantra Validator (validator.yml)
- Frontend E2E (Playwright) (frontend-e2e.yml)
- Backend CI (backend-ci.yml)
- Compose & YAML Lint (compose-yaml-lint.yml)
- Secret Scan (secret-scan.yml)

Steps (GitHub UI)

1) Navigate to: Settings → Branches → Branch protection rules → Add rule
2) Branch name pattern: `main`
3) Enable:
   - Require a pull request before merging (include code owners if used)
   - Require status checks to pass before merging
   - Search and select the checks listed above
   - (Optional) Require branches to be up to date before merging
   - (Optional) Require conversations to be resolved
   - (Optional) Require approvals (e.g., 1–2 reviewers)
4) Save changes

Frontend E2E as a required check

- The workflow is manual by default (workflow_dispatch). To make it run on PRs, add an additional trigger such as `pull_request` with a safe base url (e.g., staging) or a job that spins up a temporary environment.
- If you keep it manual, you can still mark it as a required check by running it via “Run workflow” before merging PRs that affect the frontend.

Tips

- Use environments for staging/prod deployments and add protection (reviewers) on those environments.
- If you have self-hosted runners for E2E, add them to a dedicated runner group and restrict by repo.

