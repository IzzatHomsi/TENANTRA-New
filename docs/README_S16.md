# S-16 — Observability (Prometheus metrics, /healthz, correlation IDs)

**Date:** 2025-08-09

## Backend changes
- Middleware: `CorrelationIdMiddleware` (adds `X-Request-ID` if missing).
- Metrics: `PrometheusMiddleware` with `/metrics` endpoint.
- Health: `/health` (simple) and `/healthz` (DB check).

## Docker (optional overlay)
- Prometheus (9090) scraping `backend:5000/metrics`.
- Grafana (3000) with default admin `admin/admin` (change in production).

## Apply
```bash
unzip -o tenantra_patch_S16_Observability.zip -d /path/to/tenantra-platform
cd /path/to/tenantra-platform/docker
docker compose up --build -d backend

# Start observability overlay (optional)
docker compose -f docker-compose.yml -f docker-compose.override.observability.yml up -d
```

## Validate
```bash
# Backend health
docker compose exec -T backend wget -qO- http://localhost:5000/health
docker compose exec -T backend wget -qO- http://localhost:5000/healthz

# Metrics
docker compose exec -T backend wget -qO- http://localhost:5000/metrics | head

# Prometheus UI
open http://localhost:9090

# Grafana
open http://localhost:3000  # login admin/admin
# Add Prometheus datasource at http://prometheus:9090
```
