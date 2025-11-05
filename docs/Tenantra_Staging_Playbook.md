# Tenantra Staging Deployment Playbook (HO-Docker-22)

> **Scope:** Instructions derived strictly from Phase 9 repo snapshot.

## 1. Prerequisites

- **Host:** HO-Docker-22 (Windows Server 2022 Core with Docker)
- **Required software:** Docker, Docker Compose, Git, OpenSSL

- **Firewall/DNS:** Ensure HO-Docker-22 is resolvable at `tenantra.homsi-co.com` internally and externally (FortiGate VIP for external).

- **Directories:** Repo should be cloned at `D:\Docker\tenantra-platform`

## 2. Configuration (.env)

Detected env files:

- `.env.development` → keys: APP_ENV, APP_HOST, APP_PORT, LOG_LEVEL, JWT_SECRET, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, CORS_ALLOWED_ORIGINS, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, DATABASE_URL, DB_URL ...
- `.env.production` → keys: JWT_SECRET_KEY, TENANTRA_ENC_KEY, TENANTRA_KEY_BACKUP_PASSPHRASE, TENANTRA_BACKUP_RETENTION
- `.env.staging` → keys: JWT_SECRET_KEY, TENANTRA_ENC_KEY, TENANTRA_KEY_BACKUP_PASSPHRASE, TENANTRA_BACKUP_RETENTION
For staging, create `D:\Docker\tenantra-platform\.env.staging` with keys from repo (adjust DB, JWT, SMTP, and CORS origins).

## 3. Compose Files

- `docker\docker-compose.override.health.yml` → services: backend, db
- `docker\docker-compose.override.nginx.yml` → services: nginx
- `docker\docker-compose.override.observability.yml` → services: prometheus, grafana
- `docker\docker-compose.override.worker.healthfix.yml` → services: worker
- `docker\docker-compose.override.worker.keepalive.yml` → services: worker
- `docker\docker-compose.override.worker.yml` → services: redis, worker
- `docker\docker-compose.override.yml` → services: backend, frontend, db, adminer
- `docker\docker-compose.yml` → services: db, backend, frontend, adminer

Deploy using:
```powershell
cd D:\Docker\tenantra-platform
$env:COMPOSE_PROJECT_NAME='tenantra_staging'
docker compose -f docker-compose.yml --env-file .env.staging up -d --build
```

## 4. Database Setup

- Run Alembic migrations:
```powershell
docker compose exec backend alembic upgrade head
```

- Seed database (if script exists):
```powershell
docker compose exec backend python db_seed.py
```

## 5. TLS and Nginx

- No Nginx config found. **Unknown (needs source)**.

Use Let's Encrypt certs already installed on HO-WEB-22 or generate staging self-signed certs.

## 6. Smoke Tests

After `docker compose up`, run:
```powershell
curl http://localhost:8000/health
curl http://localhost:8000/openapi.json
```

Login via UI at `https://tenantra.homsi-co.com` with seeded admin user.

## 7. Rollback Procedure

```powershell
docker compose down -v
docker volume prune -f
docker compose up -d --build
```

- DB backup/restore: Use `docker exec postgres pg_dump` and `psql -f` as needed.

## 8. Deployment Artifacts

- `.env.staging` → must be created manually
- `docker-compose.yml` and overrides → from repo
- Nginx configs (if any) → adjust `server_name` and cert paths
