# rbac.py — role helpers (normalized)
from typing import Iterable

def _norm_roles(values: Iterable[str]) -> set:
    out = set()
    for v in (values or []):
        s = str(v).strip().lower().replace(" ", "_")
        out.add(s)
    return out

def has_any_role(user_roles: Iterable[str], allowed: Iterable[str]) -> bool:
    ur = _norm_roles(user_roles)
    ar = _norm_roles(allowed)
    return bool(ur & ar)

def require_any_role(user_roles: Iterable[str], allowed: Iterable[str]) -> None:
    if not has_any_role(user_roles, allowed):
        raise ValueError(f"Forbidden: requires role in {sorted(_norm_roles(allowed))}, got {sorted(_norm_roles(user_roles))}")
