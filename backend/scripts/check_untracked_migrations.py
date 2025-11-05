"""Fail if there are untracked files under alembic/versions.

This script is intended to be run in CI (runner has git available). It exits
with non-zero status when there are any untracked files under
`backend/alembic/versions` to prevent migrations being left out of commits.
"""
import subprocess  # nosec B404: controlled git invocation
import shutil
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    versions_dir = repo_root / "alembic" / "versions"
    if not versions_dir.exists():
        print(f"alembic versions dir not found at {versions_dir}")
        return 0

    # Use `git ls-files --others --exclude-standard` limited to the versions dir
    try:
        git_exe = shutil.which("git")
        if not git_exe:
            print("git executable not found in PATH")
            return 1
        cmd = [
            git_exe,
            "ls-files",
            "--others",
            "--exclude-standard",
            str(versions_dir),
        ]
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)  # nosec B603: no shell, fixed exe
    except Exception as exc:
        print("Failed to run git to detect untracked files:", exc)
        return 1

    out = proc.stdout.strip()
    if not out:
        print("No untracked migration files found.")
        return 0

    print("ERROR: Found untracked files under alembic/versions:")
    for line in out.splitlines():
        print(" -", line)
    print("Commit these files or remove them before running CI.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
