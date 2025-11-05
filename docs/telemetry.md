# Frontend Web Vitals Telemetry

The frontend now ships browser performance metrics back to the API so we can monitor LCP/INP/CLS per tenant.

## How it works

- `frontend/src/lib/webVitals.js` posts every reported metric to `POST /api/telemetry/web-vitals` using `sendBeacon` (fallback to `fetch`).
- The payload contains name, value, rating, navigation type, timestamp, tenant/user hints (from localStorage), and the active URL.
- The backend records each event via Prometheus counters/histograms (`web_vitals_total`, `web_vital_value`) and logs the payload for downstream ingestion.

## Backend Endpoint

- Route: `backend/app/routes/telemetry.py`
- Mounted at `/telemetry/web-vitals` and `/api/telemetry/web-vitals`.
- Accepts `WebVitalPayload` schema (see `backend/app/schemas/telemetry.py`).
- Responds with `202 Accepted` and `Cache-Control: no-store`.
- Rate limited to 120 requests/minute per tenant/user/IP.

## Prometheus Metrics

- `web_vitals_total{name="LCP",rating="good"}` counts events by metric name and rating.
- `web_vital_value_sum`/`_count` expose aggregated values per metric. Configure Grafana panels to watch trend lines and percentile thresholds.

## Operational Tips

1. Add a Grafana dashboard that plots `web_vital_value` histograms for the top metrics (LCP, INP, CLS).
2. Alert on sustained `rating="poor"` growth per tenant.
3. Correlate with the request latency histogram (`http_request_duration_seconds`) to identify backend contributors.

## Privacy & Storage

- Only lightweight metadata is stored: no PII beyond tenant/user ids that are already in local storage.
- Logs are tagged under the `tenantra.telemetry` logger for ingestion into Loki/ELK.
- Ensure retention policies align with your observability data governance.
