
"""
S-7 DB Sanity: verify presence of key constraints and indexes.
Run inside container:
    python scripts/db_sanity.py
"""
import os
import sys
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not set", file=sys.stderr)
    sys.exit(2)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def has_constraint(table, name):
    cur.execute("""
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name=%s AND constraint_name=%s
    """, (table, name))
    return cur.fetchone() is not None

def has_index(name):
    cur.execute("SELECT 1 FROM pg_indexes WHERE indexname=%s", (name,))
    return cur.fetchone() is not None

checks = [
    ("constraint", "roles", "uq_roles_name"),
    ("constraint", "modules", "uq_module_name"),
    ("constraint", "users", "uq_users_username"),
    ("constraint", "users", "uq_users_email"),
    ("index", None, "ix_users_tenant_id"),
    ("index", None, "ix_users_role"),
    ("index", None, "ix_audit_logs_user_id"),
    ("index", None, "ix_audit_logs_timestamp"),
    ("index", None, "ix_assets_tenant_id"),
    ("index", None, "ix_assets_hostname"),
    ("index", None, "ix_assets_ip_address"),
]

ok = True
for kind, table, name in checks:
    if kind == "constraint":
        present = has_constraint(table, name)
    else:
        present = has_index(name)
    print(f"{kind:10} {table or '-':20} {name:30} -> {'OK' if present else 'MISSING'}")
    ok = ok and present

sys.exit(0 if ok else 1)
