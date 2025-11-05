# test_tenant_dirs.py — verifies tenant folder creation
import os, shutil, tempfile
from app.core.tenants import roots_for_tenant, ensure_tenant_roots

def test_ensure_tenant_roots(tmp_path, monkeypatch):
    # Point env to a temp structure
    monkeypatch.setenv("TENANTRA_ALLOWED_EXPORT_ROOTS", str(tmp_path / "data" / "{tenant}") + "," + str(tmp_path / "reports" / "{tenant}"))
    tenant = "acme"
    paths = ensure_tenant_roots(tenant)
    for p in paths:
        assert os.path.exists(p)
    # Ensure roots_for_tenant matches
    expected = [str(tmp_path / "data" / tenant), str(tmp_path / "reports" / tenant)]
    assert set(paths) == set(expected)
