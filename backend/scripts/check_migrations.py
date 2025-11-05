"""Quick migration verification helper used by CI.

Exit codes:
  0 - migrations appear applied and roles table exists
  1 - roles table missing or DATABASE_URL unset
"""
import os
import sys
import glob
from sqlalchemy import create_engine, text


def main() -> int:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set", file=sys.stderr)
        return 1

    print("Found alembic versions files:")
    for p in sorted(glob.glob("alembic/versions/*.py")):
        print(" -", p)

    engine = create_engine(url)
    with engine.connect() as conn:
        try:
            rows = conn.execute(text("select version_num from alembic_version")).fetchall()
            print("alembic_version:", rows)
        except Exception as ex:
            print("Could not read alembic_version table:", ex)

        r = conn.execute(text("SELECT to_regclass('public.roles')")).scalar()
        print("to_regclass(public.roles)=", r)
        if r is None:
            print("roles table is missing", file=sys.stderr)
            return 1

    print("roles table exists")
    return 0


if __name__ == '__main__':
    sys.exit(main())
