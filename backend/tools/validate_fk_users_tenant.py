"""Read-only validation: prints any FK(s) from users(tenant_id) -> tenants(id)."""
import os
from sqlalchemy import create_engine, inspect

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://tenantra:ChangeMe_DevOnly!@localhost:5432/tenantra")

def main():
    eng = create_engine(DB_URL)
    insp = inspect(eng)
    if not insp.has_table("users"):
        print("users table not found")
        return
    fks = insp.get_foreign_keys("users")
    matches = []
    for fk in fks:
        cols = fk.get("constrained_columns") or []
        ref_table = fk.get("referred_table")
        ref_cols = fk.get("referred_columns") or []
        if len(cols) == 1 and cols[0] == "tenant_id" and ref_table == "tenants" and ref_cols == ["id"]:
            matches.append({k: fk.get(k) for k in ("name","constrained_columns","referred_table","referred_columns")})
    if matches:
        print("FOUND users(tenant_id) -> tenants(id) FK(s):")
        for m in matches:
            print(m)
    else:
        print("No users(tenant_id) -> tenants(id) FK found")

if __name__ == "__main__":
    main()
