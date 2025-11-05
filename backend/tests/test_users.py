from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.database import SessionLocal
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User

client = TestClient(app)


def test_login_and_me():
    # Use the default admin password defined in the environment/seed
    response = client.post("/auth/login", data={"username": "admin", "password": "Admin@1234"})
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/users/me", headers=headers)
    assert me_response.status_code == 200
    assert "username" in me_response.json()


def _login(username: str, password: str) -> str:
    res = client.post("/auth/login", data={"username": username, "password": password})
    assert res.status_code == 200, res.text
    token = res.json().get("access_token")
    assert token
    return token


def _create_tenant(slug: str) -> Tenant:
    with SessionLocal() as session:
        tenant = session.query(Tenant).filter(Tenant.slug == slug).first()
        if tenant:
            return tenant
        tenant = Tenant(name=f"{slug}-name", slug=slug, is_active=True)
        session.add(tenant)
        session.commit()
        session.refresh(tenant)
        return tenant


def _create_user(username: str, email: str, password: str, tenant_id: int, role: str = "standard_user") -> User:
    with SessionLocal() as session:
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            session.delete(existing)
            session.commit()
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            tenant_id=tenant_id,
            role=role,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def test_admin_user_creation_is_scoped_to_tenant():
    token = _login("admin", "Admin@1234")
    username = f"user_{uuid4().hex[:8]}"
    email = f"{username}@example.com"
    payload = {
        "username": username,
        "password": "Passw0rd!",
        "email": email,
        "role": "standard_user",
    }
    res = client.post("/users", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert res.status_code == 201, res.text
    created = res.json()
    user_id = created["id"]

    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        assert user is not None
        assert user.tenant_id == 1, "Newly created users must inherit the admin tenant scope"


def test_admin_cannot_modify_user_from_other_tenant():
    tenant_slug = f"tenant-{uuid4().hex[:6]}"
    tenant = _create_tenant(tenant_slug)
    admin_username = f"{tenant_slug}-admin"
    admin_password = "Adm1n!Pass"
    admin_user = _create_user(
        username=admin_username,
        email=f"{admin_username}@example.com",
        password=admin_password,
        tenant_id=tenant.id,
        role="admin",
    )

    foreign_user = _create_user(
        username=f"foreign_{uuid4().hex[:6]}",
        email=f"foreign_{uuid4().hex[:6]}@example.com",
        password="Passw0rd!",
        tenant_id=1,
        role="standard_user",
    )

    token = _login(admin_user.username, admin_password)

    res = client.put(
        f"/users/{foreign_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "hijack@example.com"},
    )
    assert res.status_code == 404, res.text
