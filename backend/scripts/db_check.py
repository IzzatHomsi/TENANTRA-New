#!/usr/bin/env python3
"""
Database schema check script.

This utility verifies that expected tables exist in the Tenantra
database.  It is intended to be run after migrations and seeding to
ensure that the schema is in the expected state.  The script uses
SQLAlchemy's inspection API to query the database schema.  If any
expected tables are missing it will print an error and exit with a
non‑zero status code; otherwise it will print a success message.
"""

import sys
from sqlalchemy import inspect

try:
    # Import the engine from app.database, which already uses environment
    # variables to construct the connection string.
    from app.database import engine
except Exception as exc:
    print(f"Failed to import database engine: {exc}")
    sys.exit(1)


def check_tables() -> int:
    """Check for the presence of essential tables.

    Returns an exit code: 0 if all tables are present, 1 otherwise.
    """
    inspector = inspect(engine)
    # All models define their ``__tablename__`` explicitly.  Ensure
    # that the names here match the table names used in the models.
    expected_tables = ["tenants", "users", "roles", "audit_logs"]
    missing = [t for t in expected_tables if not inspector.has_table(t)]
    if missing:
        print(f"❌ Missing tables: {', '.join(missing)}")
        return 1
    print("✅ All expected tables found.")
    return 0


if __name__ == "__main__":
    sys.exit(check_tables())