# test_zipper_multi.py — tests for multi-root zipper functions
import os
from zipfile import ZipFile
from app.core.zipper import sanitize_and_validate_paths_multi, create_zip_from_paths_multi

def _touch(p, txt="x"):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt)

def test_multi_root_ok(tmp_path):
    rootA = tmp_path / "data" / "tenant1"
    rootB = tmp_path / "reports" / "tenant1"
    os.makedirs(rootA, exist_ok=True)
    os.makedirs(rootB, exist_ok=True)
    _touch(rootA / "a.txt", "A")
    _touch(rootB / "b.txt", "B")

    valid, rejected, used_roots = sanitize_and_validate_paths_multi(["a.txt", "b.txt"], [str(rootA), str(rootB)])
    assert len(valid) == 2 and not rejected
    out = tmp_path / "out.zip"
    create_zip_from_paths_multi(str(out), valid, [str(rootA), str(rootB)], arc_prefix="tenant-1")
    with ZipFile(out) as z:
        names = set(z.namelist())
        assert "tenant-1/a.txt" in names
        assert "tenant-1/b.txt" in names
