# backend/app/observability/metrics.py
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
import time
from fastapi import Request, Response
from typing import Callable
import os

# Dedicated registry (explicit to avoid accidental global pollution)
REGISTRY = CollectorRegistry(auto_describe=True)

# Request counters & latency by method/path
REQ_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
    registry=REGISTRY,
)

REQ_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    # Optional: buckets tuned via env, else sensible defaults
    buckets=tuple(
        float(x) for x in os.getenv("TENANTRA_METRIC_LATENCY_BUCKETS", "0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2,5").split(",")
    ),
    registry=REGISTRY,
)

NOTIF_SENT = Counter(
    "notifications_sent_total",
    "Notifications sent grouped by channel and status",
    ["channel", "status"],
    registry=REGISTRY,
)

SCHEDULER_RUNS = Counter(
    "scheduler_runs_total",
    "Scheduled module runs processed grouped by status",
    ["status"],
    registry=REGISTRY,
)

AUDIT_WRITES = Counter(
    "audit_logs_written_total",
    "Number of audit log entries written",
    [],
    registry=REGISTRY,
)

WEB_VITALS = Counter(
    "web_vitals_total",
    "Web vitals received from the frontend grouped by metric name and rating.",
    ["name", "rating"],
    registry=REGISTRY,
)

WEB_VITAL_VALUE = Histogram(
    "web_vital_value",
    "Distribution of web vital values grouped by metric name.",
    ["name"],
    registry=REGISTRY,
)

def request_metrics_middleware() -> Callable:
    """
    Returns an ASGI middleware function suitable for `app.middleware("http")(...)`.
    Records request count and latency with method/path/status labels.
    """
    async def _middleware(request: Request, call_next):
        method = request.method
        path = request.url.path
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = getattr(response, "status_code", 200)
            return response
        finally:
            dt = time.perf_counter() - start
            try:
                REQ_COUNT.labels(method=method, path=path, status=str(status)).inc()
                REQ_LATENCY.labels(method=method, path=path).observe(dt)
            except Exception:
                # Best-effort metrics should never break requests
                pass
    return _middleware

def metrics_endpoint() -> Callable[[Request], Response]:
    """
    Returns a FastAPI-compatible endpoint callable that produces Prometheus text.
    Using a factory avoids re-importing registry on each call.
    """
    def _endpoint(_request: Request) -> Response:
        data = generate_latest(REGISTRY)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
    return _endpoint


# Helper recording functions (import where needed)
def record_notification_delivery(channel: str, ok: bool) -> None:
    try:
        NOTIF_SENT.labels(channel=channel or "unknown", status=("sent" if ok else "failed")).inc()
    except Exception:
        pass


def record_scheduler_run(status: str) -> None:
    try:
        SCHEDULER_RUNS.labels(status=status or "unknown").inc()
    except Exception:
        pass


def record_audit_write() -> None:
    try:
        AUDIT_WRITES.inc()
    except Exception:
        pass


def record_web_vital(payload: dict) -> None:
    try:
        name = (payload.get("name") or "unknown").upper()
        rating = (payload.get("rating") or "unknown").lower()
        value = float(payload.get("value", 0))
        WEB_VITALS.labels(name=name, rating=rating).inc()
        WEB_VITAL_VALUE.labels(name=name).observe(value)
    except Exception:
        pass
