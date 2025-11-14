import pytest
from fastapi import HTTPException

from app.utils.rbac import role_required


class _RoleObj:
    def __init__(self, name: str):
        self.name = name


class _DummyUser:
    def __init__(self, role=None, roles=None):
        self.role = role
        self.roles = roles


@pytest.mark.asyncio
async def test_role_required_accepts_string_role():
    checker = role_required("admin")
    user = _DummyUser(role="admin")
    assert await checker(user=user) is True


@pytest.mark.asyncio
async def test_role_required_accepts_collection_roles():
    checker = role_required(["admin", "super_admin"])
    user = _DummyUser(roles=[_RoleObj("super_admin")])
    assert await checker(user=user) is True


@pytest.mark.asyncio
async def test_role_required_rejects_user_without_role():
    checker = role_required("admin")
    user = _DummyUser(role="viewer")
    with pytest.raises(HTTPException) as exc:
        await checker(user=user)
    assert exc.value.status_code == 403
