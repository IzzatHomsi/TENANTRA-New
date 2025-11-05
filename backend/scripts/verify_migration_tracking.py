"""Verify migration files on disk are tracked by git.

Exits non-zero if there is any mismatch between files found under
`backend/alembic/versions` and git-tracked files in the same path. This
helps ensure CI runs include all migration files.
"""
import subprocess  # nosec B404: controlled git invocation for CI checks
import shutil
import sys
from pathlib import Path


def git_tracked_versions():
    git_exe = shutil.which("git")
    if not git_exe:
        print("git executable not found in PATH")
        return None
    cmd = [git_exe, "ls-files", "backend/alembic/versions"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)  # nosec B603: no shell, fixed exe
    if proc.returncode != 0:
        print("Failed to list git-tracked files:", proc.stderr)
        return None
    paths = [p.strip() for p in proc.stdout.splitlines() if p.strip()]
    base = Path("backend") / "alembic" / "versions"
    rels = set()
    for p in paths:
        try:
            rp = Path(p)
            rel = rp.relative_to(base).as_posix()
        except Exception:
            # fallback to basename
            rel = Path(p).name
        rels.add(rel)
    return rels


def fs_versions():
    base = Path(__file__).resolve().parents[1] / "alembic" / "versions"
    if not base.exists():
        print(f"Versions directory not found at {base}")
        return set()
    rels = set()
    for p in base.rglob("*"):
        if p.is_file():
            rels.add(p.relative_to(base).as_posix())
    return rels


def main():
    tracked = git_tracked_versions()
    if tracked is None:
        return 2
    disk = fs_versions()

    missing_in_git = sorted(list(disk - tracked))
    missing_on_disk = sorted(list(tracked - disk))

    if not missing_in_git and not missing_on_disk:
        print("Migration tracking OK: tracked files match files on disk.")
        return 0

    if missing_in_git:
        print("ERROR: The following migration files exist on disk but are NOT tracked by git:")
        for f in missing_in_git:
            print(" -", f)

    if missing_on_disk:
        print("ERROR: The following files are tracked by git but missing on disk:")
        for f in missing_on_disk:
            print(" -", f)

    print("Commit missing files or remove stale tracked entries. Failing CI.")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
