# verify_alembic_single_head.py
"""
Utility script to ensure Alembic has only ONE active head.
Prevents migration conflicts caused by multiple parallel heads.

Usage:
    python verify_alembic_single_head.py
"""

import os
import sys
import subprocess

# Ensure we run inside the backend container path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALEMBIC_DIR = os.path.join(BASE_DIR, "alembic")

def run_alembic_heads():
    """Run `alembic heads` and return the output."""
    try:
        result = subprocess.run(
            ["alembic", "heads"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("❌ Error running alembic heads:", e.stderr)
        sys.exit(1)

def verify_single_head():
    """Verify that only one Alembic head exists."""
    output = run_alembic_heads()
    heads = [line.split(" ")[0] for line in output.splitlines() if line.strip()]
    
    if len(heads) == 0:
        print("⚠️  No Alembic heads found. Run `alembic revision --autogenerate` to create one.")
        sys.exit(1)
    elif len(heads) > 1:
        print("❌ Multiple Alembic heads detected:", heads)
        print("👉 Fix by merging them:")
        print(f"   alembic merge -m 'merge multiple heads' {' '.join(heads)}")
        sys.exit(1)
    else:
        print(f"✅ Single Alembic head verified: {heads[0]}")

if __name__ == "__main__":
    verify_single_head()
