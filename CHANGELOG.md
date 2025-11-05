# CHANGELOG — S-16 Observability

## Added
- `app/middleware/correlation_id.py` — sets/propagates `X-Request-ID`.
- `app/observability/metrics.py` — Prometheus middleware + `/metrics` endpoint.
- `app/routes/healthz.py` — `/healthz` DB check.
- `docker/prometheus/prometheus.yml` and `docker/docker-compose.override.observability.yml` — Prometheus+Grafana overlay.

## Changed
- `app/main.py` — wires new middleware and endpoints; exempts `/metrics`, `/health`, `/healthz` from auth in OpenAPI.

## Validation
- `/metrics` exposes `http_requests_total` and `http_request_duration_seconds`.
- `/healthz` returns `{"status":"ok","db":"up"}` when DB reachable.
- Prometheus scrapes backend; Grafana reachable on :3000.
