
# DEPLOY — End‑to‑End (Dev → Staging → Prod)

## Prereqs
- Docker + docker compose v2
- Postgres reachable per your `DATABASE_URL`
- Secrets set in CI or `.env` (see ENV MATRIX below)
- GitHub Actions secrets for staging (see **CI/CD Secrets**)

## Order of Operations
1. **S‑1_2**: backend API auth/users, Alembic merge; restart stack.
2. **S‑3**: frontend refresh; rebuild `frontend` service.
3. **S‑4**: notifications API + UI; no restart beyond backend if needed.
4. **S‑5**: structured logging + router includes; restart backend.
5. **S‑6**: RBAC/frontend gating; apply front changes.
6. **S‑7**: DB indexes/uniques; `alembic upgrade head`.
7. **S‑8**: enable GitHub Actions quality gates (optional local pre‑commit).
8. **S‑9**: roles API + seeds; run `python scripts/db_seed.py`; add healthchecks overlay.
9. **S‑10**: background worker overlay; start `worker` service.
10. **S‑11/12**: access logs + security headers + strict CORS + rate limiting; restart backend.
11. **S‑13**: Nginx reverse‑proxy overlay with TLS.

## Quick Apply (per patch ZIP)
```bash
# Example for S-1/2
unzip -o patches/tenantra_patch_S1_S2_merged.zip -d /path/to/tenantra-platform
cd /path/to/tenantra-platform/docker
docker compose up --build -d

# After any DB‑affecting patch
docker compose exec -T backend alembic upgrade head
```

## Docker Overlays
- Healthchecks: `-f docker-compose.yml -f docker-compose.override.health.yml`
- Worker:      `-f docker-compose.yml -f docker-compose.override.worker.yml`
- Nginx:       `-f docker-compose.yml -f docker-compose.override.nginx.yml`

## ENV MATRIX (minimum)
Backend:
```
DATABASE_URL=postgresql+psycopg2://user:pass@db:5432/tenantra
CORS_ALLOWED_ORIGINS=https://tenantracloud.com,https://tenantra.homsi-co.com
CORS_MODE=strict
LOG_DIR=/app/logs
LOG_LEVEL=INFO
LOG_FORMAT=json
JWT_SECRET=***
JWT_ALG=HS256
JWT_EXPIRE_MINUTES=60

# SMTP (S-4/S-10)
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...
SMTP_FROM=notifications@tenantra.example
SMTP_TLS=true

# Rate limiting (S-12)
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_WINDOW=900
RATE_LIMIT_OVERRIDES=/auth/login:10/60
```

Worker (overlay):
```
WORKER_POLL_INTERVAL=5
WORKER_MAX_ATTEMPTS=5
WORKER_BACKOFF_BASE=5
WORKER_BACKOFF_FACTOR=2.0
```

Nginx (overlay): place certs under `./certs/fullchain.pem`, `./certs/privkey.pem`.

---

## Local development

1. Copy `.env.development` and adjust anything tenant-specific if required.
2. Start the stack (backend, frontend, postgres, adminer):

   ```bash
   make up        # docker compose up with the override
   ```

3. Apply migrations and seed the database:

   ```bash
   make migrate
   make seed
   ```

4. Visit `http://localhost:5173` for the frontend and `http://localhost:5000/health` for the backend health probe.

Use `make down` or `make clean` to stop/clean containers when finished.

---

## CI/CD Secrets

Set the following GitHub Actions secrets in the repository for staging deployments:

| Secret | Description |
| --- | --- |
| `STAGING_SSH_HOST` | IP or hostname of HO-Docker-22 |
| `STAGING_SSH_USER` | SSH username with deploy privileges |
| `STAGING_SSH_KEY`  | Private key (PEM, no passphrase) |
| `STAGING_REMOTE_DIR` | Absolute path of the cloned repo on the server (e.g. `/opt/tenantra-platform`) |
| `STAGING_ENV_FILE` | Multi-line contents of the staging `.env` (use the template in `.env.staging`) |

Optional E2E smoke tests require `E2E_ADMIN_USER`, `E2E_ADMIN_PASS`, `E2E_STD_USER`, and `E2E_STD_PASS`.

---

## GitHub Actions Workflow Overview

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `backend-ci.yml` | PR / push touching backend or docker | Lint (ruff), type-check (mypy), security (bandit) + pytest against ephemeral Postgres |
| `frontend-ci.yml` | PR / push touching frontend | Build + ESLint |
| `compose-yaml-lint.yml` | PR / push with YAML changes | Validate docker compose files + yamllint |
| `secret-scan.yml` | PR / push | gitleaks scan |
| `deploy-staging.yml` | Push to `main` / manual | Git pull on HO-Docker-22, rebuild containers, run migrations + seed, health smoke checks |
| `post-deploy-probes.yml` | Manual | HTTPS smoke probes against staging |
| `tenantra-sr1.yml` | Manual / backend changes | Regression tests for tenant export logic |

`deploy-staging` expects the repository to already exist on the host. The workflow uploads the `.env` provided via secret and runs `docker compose` with the staging nginx overlay.
## Grafana via Nginx (staging)

Grafana is exposed at `https://Tenantra.homsi-co.com/grafana/` behind basic auth.

- Create the htpasswd file on the host (do NOT commit):
  - Path: `D:\Docker\tenantra-platform\docker\nginx\includes\staging\htpasswd_grafana`
  - Contents: one or more `user:hash` lines in Apache htpasswd format.
  - You can generate offline and paste via secret (`GRAFANA_BASIC_HTPASSWD`).

- Environment for Grafana provisioning (optional):
  - `GRAFANA_ALERT_EMAILS` for default contact point (comma-separated).

- After deploy, open:
  - Grafana: `https://Tenantra.homsi-co.com/grafana/`
  - Overview dashboard: `/grafana/d/tenantra-overview/tenantra-overview?orgId=1`
