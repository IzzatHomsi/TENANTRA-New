# backend/app/core/tenants.py
# Tenant helpers: derive a user's tenant scope safely.

import os
from dataclasses import dataclass
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.models.user import User


@dataclass(frozen=True)
class TenantScope:
    id: int
    slug: str


def _allowed_root_templates() -> Sequence[str]:
    raw = os.getenv("TENANTRA_ALLOWED_EXPORT_ROOTS")
    if not raw:
        return ("/app/data/tenants/{tenant}",)
    return tuple(filter(None, (part.strip() for part in raw.split(","))))


def roots_for_tenant(tenant: str | int) -> list[str]:
    slug = str(tenant)
    paths: list[str] = []
    for template in _allowed_root_templates():
        path = template.replace("{tenant}", slug)
        paths.append(os.path.abspath(path))
    return paths


def ensure_tenant_roots(tenant: str | int) -> list[str]:
    paths = roots_for_tenant(tenant)
    for p in paths:
        os.makedirs(p, exist_ok=True)
    return paths


def get_user_tenant_scope(user: User, db: Optional[Session] = None) -> Optional[TenantScope]:
    """
    Resolve the current user's tenant scope.
    - If user.tenant_id is present, load Tenant to get slug (requires db).
    - If db is None, fall back to a generic slug based on tenant_id.
    - Returns None when no tenant is associated.
    """
    if not user or not getattr(user, "tenant_id", None):
        return None

    tenant_id = int(user.tenant_id)
    if db is not None:
        tenant = db.query(Tenant).get(tenant_id)
        slug = (tenant.slug or f"tenant{tenant_id}") if tenant else f"tenant{tenant_id}"
    else:
        slug = f"tenant{tenant_id}"

    return TenantScope(id=tenant_id, slug=slug)
