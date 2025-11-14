# Tenantra Operations Runbook

This runbook captures the day-to-day developer and operator workflow for Tenantra: how to bring the stack up, rebuild it safely, run migrations, and validate functionality before shipping.

---

## 1. Environment & Prerequisites

| Requirement | Notes |
| --- | --- |
| Python 3.11 | `pip install -r backend/requirements.txt` |
| Node.js 20+ | `npm install` inside `frontend/` (or `npm ci` in CI) |
| Docker + Compose | Required for composed services & menu tooling |
| `.env` files | Seed from `.env.example`, then copy to `.env.development`, `.env.staging`, etc. Ensure `TENANTRA_ENC_KEY` and `JWT_SECRET` are unique per environment. |

Key environment variables:

- **Backend security**: `TENANTRA_ENC_KEY`, `JWT_SECRET`, `TENANTRA_ADMIN_PASSWORD`
- **Database**: `DATABASE_URL` / `DB_URL`
- **Background workers**: `TENANTRA_ENABLE_NOTIFICATIONS_WORKER`, `TENANTRA_ENABLE_MODULE_SCHEDULER`
- **Frontend**: `VITE_API_URL`, `VITE_REMOTE_MODULE_CATALOG_URL`
- **Testing**: `TENANTRA_TEST_ADMIN_PASSWORD`, `TENANTRA_TEST_DB_URL`

---

## 2. Container Control

Use `tenantra_control_menu.sh` for deterministic stack operations. The script auto-discovers overrides and injects health checks.

```bash
./tenantra_control_menu.sh --repo-root "$(pwd)" --no-pause
```

### Common options

| Option | When to use |
| --- | --- |
| `1` – Full setup | Rebuild + up + migrate + seed. Use at the start of a phase or after major dependency changes. |
| `6` – Rebuild | Rebuild images without seeding. Useful after backend/frontend dependency tweaks. |
| `4` / `5` – Stop or Clean | Clean shutdown (`4`) or nuking volumes (`5`). |
| `7-9` | Alembic status & upgrades. |
| `A` | Seed default tenant/admin (uses `SEED_*` env vars). |
| `B/L/T` | Backend + Nginx smoke tests. |

**Full rebuild flow (option `1`):**
1. Ensure `.env.<TENANTRA_ENV>` is up to date.
2. Run option `1`. The script builds all containers, applies migrations, and seeds defaults.
3. Watch for errors in the summarized step list. Rerun failing steps via their letter/number.
4. After success, hit `http://localhost` (or the configured domain) and sign in with the seeded admin.

---

## 3. Local Development Workflow

1. **Sync deps**
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```
2. **Start the stack** – either via `make up` or the control menu (option `1` or `2`).
3. **Iterate**
   - Backend: `cd backend && uvicorn app.main:create_app --factory --reload`
   - Frontend: `cd frontend && npm run dev -- --host`
4. **Apply DB changes**
   ```bash
   make migrate
   make seed    # idempotent; keeps default tenant/admin current
   ```

---

## 4. Testing & Validation

### Consolidated suite

`make test-all` (new Sprint 3 command) runs:

1. Backend `pytest -q`
2. Frontend Playwright UI specs (`tests/moduleCatalog*.spec.ts`)
3. Playwright E2E specs (`tests/e2e/**`)

Usage:
```bash
TENANTRA_TEST_ADMIN_PASSWORD=Admin@1234 make test-all
```

This is the same command executed by the `Full Stack Tests` GitHub workflow on every pull request.

### Targeted commands

- Backend only: `cd backend && pytest -q`
- Frontend Playwright: `cd frontend && TENANTRA_TEST_ADMIN_PASSWORD=... npm run test:e2e`
- Lighthouse budgets: `cd frontend && npm run test:lighthouse`
- Validation sweep: `python tools/validate_tenantra.py --output-dir reports`

Always regenerate `openapi.json` (`python backend/tools/generate_openapi.py --output openapi.json`) if API schemas changed.

---

## 5. Troubleshooting & Observability

| Scenario | Checklist |
| --- | --- |
| **Login fails** | Confirm `TENANTRA_ADMIN_PASSWORD`/`TENANTRA_TEST_ADMIN_PASSWORD` set, rerun seed (`option A`), inspect backend logs via control menu logs submenu. |
| **Migrations stuck** | `docker compose logs backend` for Alembic output, run `option 7/8/9` or `make migrate`. Ensure Alembic head matches repo (`backend/alembic/versions`). |
| **Workers misbehave** | Verify `TENANTRA_ENABLE_MODULE_SCHEDULER` / `TENANTRA_ENABLE_NOTIFICATIONS_WORKER` flags. Use menu option `W` to enable the notifications worker overrides. |
| **Slow UI** | Run `npm run build:report` and inspect `dist/bundle-analysis.html`. Optionally enable `ANALYZE=true` with Vite build for deeper stats. |
| **Health checks** | Menu options `B` (backend sanity) and `L` (Nginx smoke). For API-only, `curl http://localhost:5000/healthz`. |

Logs & metrics:
- Containers log path: `docker logs <service>` or menu logs submenu (`G`).
- Prometheus/Grafana: set `TENANTRA_GRAFANA` and `TENANTRA_VALIDATE_GRAFANA=1`, then run `make validate`.
- Structured backend logs configured via `TENANTRA_LOG_TO_FILE=1` (writes under `/app/logs` in containers).

---

## 6. Release Checklist Snippet

1. `git status` clean (excluding intentional changes).
2. `make test-all` green locally.
3. Control menu option `1` (or at least `6` + `2`) with no failures.
4. Update `docs/Tenantra_Master_Brain_v1.0.md` + relevant docs.
5. Regenerate `openapi.json` if API changed.
6. Attach verification commands (`make test-all`, `npm run test:e2e`, etc.) to PR description.

Keep this runbook updated whenever operational tooling or workflows change.
