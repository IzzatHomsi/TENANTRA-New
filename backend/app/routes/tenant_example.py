from fastapi import APIRouter
from app.api.tenant_example import router as api_router

# Expose router under app.routes.* for automatic inclusion in main.create_app
router = APIRouter()
router.include_router(api_router, prefix="")
