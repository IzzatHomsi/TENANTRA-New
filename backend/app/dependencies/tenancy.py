"""Reusable tenant-scope dependencies."""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Query, status

from app.core.auth import get_current_user
from app.models.user import User


def tenant_scope_dependency():
    """FastAPI dependency factory to resolve the effective tenant scope.

    Tenant users are forced to operate within their tenant. MSP/global users
    (tenant_id is None) must provide the explicit tenant_id query parameter.
    """

    def _resolver(
        tenant_id: Optional[int] = Query(
            None,
            description="Tenant scope (required for MSP/global administrators)",
        ),
        current_user: User = Depends(get_current_user),
    ) -> int:
        user_tenant = getattr(current_user, "tenant_id", None)
        if user_tenant is None:
            if tenant_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="tenant_id is required for global administrators",
                )
            return tenant_id
        if tenant_id is not None and tenant_id != user_tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden tenant scope",
            )
        return user_tenant

    return _resolver


def ensure_same_tenant(resource_tenant_id: Optional[int], current_user: User) -> None:
    """Raise if the resource does not belong to the current user's tenant."""
    if resource_tenant_id is None:
        return
    user_tenant = getattr(current_user, "tenant_id", None)
    if user_tenant is None:
        return
    if resource_tenant_id != user_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden tenant scope",
        )
