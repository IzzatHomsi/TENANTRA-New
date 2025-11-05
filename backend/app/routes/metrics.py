# Expose Prometheus metrics at GET /metrics (and /api/metrics via dual mount)
from fastapi import APIRouter, Request, Response
from app.observability.metrics import metrics_endpoint

router = APIRouter(tags=["Observability"])

# The factory returns a callables that accepts (Request) -> Response
_metrics_handler = metrics_endpoint()

@router.get("/metrics")
def metrics(request: Request) -> Response:
    return _metrics_handler(request)
