#!/usr/bin/env python3
"""Lightweight Alembic head verifier.

This script inspects backend/alembic/versions and ensures there's exactly one
head revision. It uses Alembic's ScriptDirectory when alembic is installed,
otherwise it falls back to parsing the migration files with ast so CI can run
the check without additional dependencies.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
ALEMBIC_DIR = BACKEND_DIR / "alembic"
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
VERSIONS_DIR = ALEMBIC_DIR / "versions"


def _heads_via_alembic() -> Optional[List[str]]:
    try:
        from alembic.config import Config  # type: ignore
        from alembic.script import ScriptDirectory  # type: ignore
    except Exception:
        return None
    cfg = Config(str(ALEMBIC_INI)) if ALEMBIC_INI.exists() else Config("backend/alembic.ini")
    script = ScriptDirectory.from_config(cfg)
    return list(script.get_heads())


def _heads_via_ast() -> List[str]:
    parents: Dict[str, Optional[str]] = {}
    children: Dict[Optional[str], Set[str]] = {}
    for path in sorted(VERSIONS_DIR.glob("*.py")):
        if path.name.startswith("_"):
            continue
        with path.open("r", encoding="utf-8") as handle:
            tree = ast.parse(handle.read(), filename=str(path))
        revision = None
        down_revision = None
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and target.id == "revision":
                        revision = ast.literal_eval(node.value)  # type: ignore[arg-type]
                    if isinstance(target, ast.Name) and target.id == "down_revision":
                        down_revision = ast.literal_eval(node.value) if node.value is not None else None  # type: ignore[arg-type]
        if revision is None:
            continue
        parents[revision] = down_revision
        children.setdefault(down_revision, set()).add(revision)
    heads = [rev for rev in parents.keys() if rev not in children]
    return heads


def main() -> int:
    versions = list(VERSIONS_DIR.glob("*.py"))
    if not versions:
        print("No Alembic versions found under backend/alembic/versions", file=sys.stderr)
        return 1

    heads = _heads_via_alembic() or _heads_via_ast()
    if len(heads) != 1:
        print(f"Detected multiple Alembic heads: {heads}", file=sys.stderr)
        print("Run `alembic heads` to inspect and create a merge revision.", file=sys.stderr)
        return 1
    print(f"Alembic head verified: {heads[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
