import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.base import Base
from app.models.tenant import Tenant
from app.database import get_db


def _create_test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return engine, Session


def test_tenant_lookup_by_slug_and_id():
    engine, Session = _create_test_db()
    # create a tenant
    with Session() as s:
        t = Tenant(name="Acme Inc", slug="acme", is_active=True)
        s.add(t)
        s.commit()
        s.refresh(t)

    # override dependency
    def _get_test_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    client = TestClient(app)

    # lookup by slug via header
    resp = client.get("/tenant-example", headers={"X-Tenant-Slug": "acme"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["tenant_input"] == "acme"
    assert data["tenant"]["slug"] == "acme"

    # lookup by id via query param
    tenant_id = str(t.id)
    resp2 = client.get(f"/tenant-example?tenant_id={tenant_id}")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["tenant_input"] == tenant_id
    assert data2["tenant"]["id"] == t.id

    # cleanup override
    app.dependency_overrides.pop(get_db, None)


def test_tenant_none():
    client = TestClient(app)
    resp = client.get("/tenant-example")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tenant_input"] is None
    assert data["tenant"] is None
