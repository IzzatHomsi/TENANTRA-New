# Runtime Secrets

Create the following files before running `docker compose`:

- `db_password.txt` — PostgreSQL superuser password.
- `redis_password.txt` - Redis `requirepass` secret.
- `grafana_admin_password.txt` - Initial Grafana admin password.

Backend/Grafana reuse:

- `grafana_admin_user.txt` — Grafana admin username used by both Grafana and the backend’s Grafana proxy/checks via `GRAFANA_USER_FILE`.
- `grafana_admin_password.txt` — Reused by Grafana and the backend via `GRAFANA_PASS_FILE` for upstream Basic Auth.

Notes:

- Place one value per file with no trailing newline.
- Dev/staging overlays mount these secrets into the backend so `/api/admin/observability/grafana/*` and `/grafana/*` can authenticate to secured Grafana.

Each file should contain the secret value with no trailing newline. Store them outside of version control; this directory ignores `*.txt` files by default.
