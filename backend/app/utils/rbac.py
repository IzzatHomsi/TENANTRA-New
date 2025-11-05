# backend/app/utils/rbac.py
# Back-compat RBAC dependency that tolerates several legacy calling styles.
# IMPORTANT: No starlette Request types in the dependency signature to avoid
# Pydantic response-model confusion in some FastAPI/Pydantic combos.

from typing import Iterable, List, Union
from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user
from app.core.rbac import has_any_role


def _normalize_roles(roles: Union[str, Iterable[str], None], extra: Iterable[str]) -> List[str]:
    vals: List[str] = []
    if roles is None:
        pass
    elif isinstance(roles, str):
        vals.append(roles)
    else:
        vals.extend(list(roles))
    vals.extend(list(extra))
    # normalize to snake_case-ish
    return [str(r).strip().lower().replace(" ", "_") for r in vals if str(r).strip()]


def role_required(
    roles: Union[str, Iterable[str], None] = None,
    *extra_roles: str,
    require_all: bool = False,
):
    """
    Works with:
      - dependencies=[Depends(role_required(["admin"]))]
      - dependencies=[Depends(role_required("admin"))]
      - dependencies=[Depends(role_required, ["admin"])]  # tolerated legacy misuse
    """
    normalized = _normalize_roles(roles, extra_roles)

    async def _check(user=Depends(get_current_user)):
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        if not normalized:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not specified")

        ok = all(has_any_role(user, [r]) for r in normalized) if require_all else has_any_role(user, normalized)
        if not ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return True

    return _check
