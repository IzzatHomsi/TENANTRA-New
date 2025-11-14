# Tenantra – Unified IT Discovery, Compliance, and Automation

Tenantra is a multi-tenant FastAPI + React platform that inventories complex environments, enforces compliance controls, orchestrates scanning modules, and powers MSP-ready dashboards.

---

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```
2. **Seed environment variables**
   ```bash
   cp .env.example .env.development   # adjust secrets before use
   ```
3. **Bring the stack up** (build + migrate + seed) via the menu:
   ```bash
   ./tenantra_control_menu.sh --repo-root "$(pwd)" --no-pause    # choose option 1
   ```
4. Sign in at `http://localhost` with the seeded admin credentials (`TENANTRA_ADMIN_PASSWORD`).

For manual Compose control you can still run `make up`, `make down`, `make migrate`, and `make seed` directly.

---

## Daily Commands

| Command | Purpose |
| --- | --- |
| `make up` / `make down` | Start/stop the Docker stack with the standard overrides. |
| `make migrate` | Apply Alembic migrations to the configured database. |
| `make seed` | Re-seed the default tenant + admin (idempotent). |
| `make test-all` | Run backend pytest + frontend Playwright UI + Playwright E2E suites. |
| `cd backend && uvicorn app.main:create_app --factory --reload` | Local API iteration. |
| `cd frontend && npm run dev -- --host` | Vite dev server (uses unified `vite.config.js`). |
| `cd frontend && npm run build:module-catalog-remote` | Build the module catalog federation remote (`vite build --mode catalog-remote`). |
| `cd frontend && npm run build:ssr` | Build the SSR bundle (`vite build --mode ssr`). |

Need a full operational walkthrough? → See `docs/RUNBOOK.md`.

---

## Testing & CI

- `make test-all` is the canonical verification command and is executed automatically by `.github/workflows/test-all.yml` on every pull request.
- Targeted commands: `cd backend && pytest -q`, `cd frontend && TENANTRA_TEST_ADMIN_PASSWORD=... npm run test:frontend`, `npm run test:e2e`, `npm run test:lighthouse`.
- Use `python tools/validate_tenantra.py --output-dir reports` for the cross-cutting validation sweep (CORS, headers, health checks, etc.).

---

## Documentation Map

| File | Description |
| --- | --- |
| [`Tenantra_Unified_Project_and_Rollout_Plan.md`](Tenantra_Unified_Project_and_Rollout_Plan.md) | Phase-by-phase scope, architecture, and rollout plan. |
| [`docs/Tenantra_Master_Brain_v1.0.md`](docs/Tenantra_Master_Brain_v1.0.md) | Deep technical reference for modules, tenancy, and operational patterns. |
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | Hands-on operations guide (stack control, testing, troubleshooting). |
| [`docs/DEV_STACKS.md`](docs/DEV_STACKS.md) | Compose overlays and environment profiles. |
| [`docs/FAQ.md`](docs/FAQ.md) | Frequently asked questions across auth, modules, and onboarding. |
| [`docs/Tenantra_Staging_Playbook.md`](docs/Tenantra_Staging_Playbook.md) | Staging rollout + verification checklist. |
| [`MERGED_TASK_LIST.md`](MERGED_TASK_LIST.md) | Active sprint/phase tasks (current phase: Sprint 3). |

---

## Contributing & Support

- Review the guardrails in [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) before pushing code.
- Follow commit naming (`P#_B#`: description) and always attach `make test-all` output to PRs.
- Questions or bugs? Open an issue on GitHub and reference the relevant sprint task.

Tenantra is licensed under the MIT License. See [LICENSE](LICENSE) for details.
