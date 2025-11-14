# backend/app/utils/rbac.py
# Back-compat RBAC dependency that tolerates several legacy calling styles.
# IMPORTANT: No starlette Request types in the dependency signature to avoid
# Pydantic response-model confusion in some FastAPI/Pydantic combos.

from typing import Iterable, List, Sequence, Set, Union, Any
from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user


def _norm_role_set(values: Iterable[str]) -> Set[str]:
    normalized: Set[str] = set()
    for value in values or []:
        if value is None:
            continue
        normalized.add(str(value).strip().lower().replace(" ", "_"))
    return normalized


def has_any_role(user_roles: Iterable[str], allowed: Iterable[str]) -> bool:
    """
    Returns True if any of the user's roles intersects the allowed list.
    """
    return bool(_norm_role_set(user_roles) & _norm_role_set(allowed))


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


def _stringify_role(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    for attr in ("name", "role", "slug"):
        attr_val = getattr(value, attr, None)
        if attr_val:
            return str(attr_val)
    return str(value)


def _extract_user_roles(user: Any) -> List[str]:
    if user is None:
        return []
    collected: List[str] = []

    def _extend(values: Union[Sequence[Any], Any, None]) -> None:
        if values is None:
            return
        if isinstance(values, (list, tuple, set)):
            for item in values:
                collected.append(_stringify_role(item))
        else:
            collected.append(_stringify_role(values))

    _extend(getattr(user, "roles", None))
    primary = getattr(user, "role", None)
    if primary:
        collected.append(_stringify_role(primary))
    fallback = getattr(user, "role_name", None)
    if fallback:
        collected.append(_stringify_role(fallback))

    return [value for value in collected if value]


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

        user_roles = _extract_user_roles(user)
        ok = all(has_any_role(user_roles, [r]) for r in normalized) if require_all else has_any_role(user_roles, normalized)
        if not ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return True

    return _check
