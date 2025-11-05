#!/usr/bin/env python3
"""
Generate the OpenAPI JSON for the Tenantra FastAPI app.

Usage:
  python backend/tools/generate_openapi.py --output openapi.json

Notes:
- This imports the FastAPI app without starting any server.
- It writes a stable, pretty-printed JSON to the given output path.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Path to write openapi.json")
    args = parser.parse_args()

    # Ensure we can import backend app
    repo_root = Path(__file__).resolve().parents[2]
    backend_dir = repo_root / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    # Import the app and render schema
    try:
        from app.main import app  # type: ignore
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: failed to import app.main: {exc}", file=sys.stderr)
        return 2

    # Force build of OpenAPI (customized in app.main)
    schema = app.openapi()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")
    print(f"Wrote OpenAPI schema to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

