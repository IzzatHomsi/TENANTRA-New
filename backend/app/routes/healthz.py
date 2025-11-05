# backend/app/routes/healthz.py
from fastapi import APIRouter
from .health import health  # reuse

router = APIRouter(tags=["Health"])

@router.get("/healthz")
def healthz():
    # Traditional kube-style alias
    return health()
