# test_zipper.py
# Purpose: Unit tests for zipper utility without needing a running API server.
import os, tempfile, shutil
from app.core.zipper import sanitize_and_validate_paths, create_zip_from_paths
from zipfile import ZipFile

def _touch(p: str, text: str = "x"):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)

def test_sanitize_and_create_zip(tmp_path):
    # Arrange: make a small tree under allowed root
    allowed = tmp_path / "root"
    os.makedirs(allowed, exist_ok=True)
    _touch(str(allowed / "a.txt"), "A")
    _touch(str(allowed / "sub" / "b.txt"), "B")

    # Valid relative paths (one file and one dir), and some rejected ones
    valid, rejected = sanitize_and_validate_paths(["a.txt", "sub", "/etc/passwd", "../escape"], str(allowed))
    assert str(allowed / "a.txt") in valid
    assert any(reason for p, reason in rejected if p == "/etc/passwd")

    # Create the zip
    out = tmp_path / "out.zip"
    create_zip_from_paths(str(out), valid, base_root=str(allowed), arc_prefix="tenant-1")
    assert os.path.exists(out)

    # Verify contents
    with ZipFile(out) as z:
        names = set(z.namelist())
        assert "tenant-1/a.txt" in names
        assert "tenant-1/sub/b.txt" in names
