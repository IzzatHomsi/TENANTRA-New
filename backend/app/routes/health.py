# backend/app/routes/health.py
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
def health() -> dict:
    """Primary liveness probe for orchestrators."""
    return {"status": "OK"}

@router.get("/health/ping")
def health_ping() -> dict:
    """Backwards-compatible alias expected by legacy scripts."""
    return health()
