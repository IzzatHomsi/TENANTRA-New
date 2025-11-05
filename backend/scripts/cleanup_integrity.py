#!/usr/bin/env python3
"""
Cleanup script for integrity tables based on tenant retention policies.

Reads DATABASE_URL/DB_URL and removes old rows from:
- registry_snapshots, service_snapshots, task_snapshots, boot_configs, integrity_events

Retention days per tenant is read from TenantRetentionPolicy, defaulting to 30.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
import argparse


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=None, help="Override retention days for all tenants")
    ap.add_argument("--tenant", type=int, default=None, help="Only clean this tenant id")
    ap.add_argument("--cutoff", type=str, default=None, help="Override cutoff ISO timestamp (utc)")
    args = ap.parse_args()
    url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not url:
        print("ERROR: DATABASE_URL/DB_URL not set")
        return 2
    engine = create_engine(url)
    with engine.begin() as conn:
        # Fetch per-tenant retention in days; fallback 30
        policies = {}
        try:
            if args.days is None:
                for row in conn.execute(text("select tenant_id, integrity_days from tenant_retention_policies")):
                    policies[int(row[0])] = int(row[1] or 30)
        except Exception:
            pass
        # Fallback for all tenants if table not present
        if args.days is not None:
            tids = [args.tenant] if args.tenant is not None else [r[0] for r in conn.execute(text("select id from tenants"))]
            for tid in tids:
                policies[int(tid)] = int(args.days)
        elif not policies:
            # Guess tenants
            tids = [args.tenant] if args.tenant is not None else [r[0] for r in conn.execute(text("select id from tenants"))]
            for tid in tids:
                policies[int(tid)] = 30

        now = datetime.utcnow()
        total_deleted = 0
        # strict allowlist of tables and timestamp columns to avoid SQL injection
        allowed_tables = {
            "registry_snapshots": "collected_at",
            "service_snapshots": "collected_at",
            "task_snapshots": "collected_at",
            "boot_configs": "collected_at",
            "integrity_events": "detected_at",
        }
        for tenant_id, days in policies.items():
            cutoff = (datetime.fromisoformat(args.cutoff) if args.cutoff else (now - timedelta(days=max(1, days))))
            cutoff_s = cutoff.isoformat()
            for table, ts_col in allowed_tables.items():
                try:
                    # table and ts_col are taken from allowlist above to avoid injection
                    # Bandit: table/column names are whitelisted above; bindings used for values
                    stmt = text(f"delete from {table} where tenant_id=:tid and {ts_col} < :cut")  # nosec B608
                    res = conn.execute(stmt, {"tid": tenant_id, "cut": cutoff_s})
                    total_deleted += res.rowcount or 0
                except Exception as e:
                    print(f"WARN: failed cleanup for {table}: {e}")
        print(f"Cleanup complete: deleted {total_deleted} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
