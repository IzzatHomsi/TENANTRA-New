# CI/CD Workflows & Gates Summary

## Generated Workflows
- `.github/workflows/backend-ci.yml`  
- `.github/workflows/frontend-ci.yml`  
- `.github/workflows/compose-yaml-lint.yml`  
- `.github/workflows/secret-scan.yml`  
- `.github/workflows/deploy-staging.yml`  
- `.github/workflows/post-deploy-probes.yml`  

---

## Required Secrets
For **staging deploy**:
- `STAGING_SSH_HOST` → HO-Docker-22 IP/FQDN  
- `STAGING_SSH_USER` → SSH username  
- `STAGING_SSH_KEY` → private key (PEM format, no passphrase)  

For **optional secret scan**:
- *(none required unless enterprise license is used)*  

---

## Gates & Branch Protections
1. Protect the `main` branch.  
2. Require **pull requests** to merge into `main`.  
3. Mark the following jobs as **required checks** before merging:  
   - ✅ Backend CI  
   - ✅ Frontend CI  
   - ✅ Compose & YAML Lint  
   - ✅ Secret Scan  
4. Optionally require **environment approval** for `Deploy Staging`.  

---

## Pipeline Flow
1. **CI Layer** (runs on PR & push to `main`):  
   - Lint (Python & JS/TS)  
   - Type check (mypy)  
   - Security scan (bandit, gitleaks)  
   - Unit tests (pytest, npm test if available)  
   - Compose config validation & yamllint  

2. **Deploy Layer** (on merge to `main` or manual trigger):  
   - SSH into HO-Docker-22  
   - `git pull` + `docker compose up -d --build`  
   - Alembic migrations + DB seed  
   - Smoke tests: `/health`, `/openapi.json`  

3. **Post-Deploy Layer** (manual trigger or scheduled):  
   - HTTPS probes to staging URL  
   - CORS preflight check on `/auth/login`  

---

## Post-Deploy Automated Probes
- `GET /health` → expect `200 OK`  
- `GET /openapi.json` → valid OpenAPI spec JSON  
- `OPTIONS /auth/login` → CORS headers present (Origin = `https://tenantra.homsi-co.com`)  

## Container image security gates

- `container-security.yml` builds `tenantra/backend` and `tenantra/frontend` images using the hardened Dockerfiles.
- `docker scout cves` runs with `--only-severity critical,high` and fails the job if findings remain; SARIF reports upload to code scanning.
- `aquasecurity/trivy-action` enforces that no Critical findings and at most High (when unpatched upstream) are present before the pipeline proceeds.
