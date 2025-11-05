# S-17 — Performance & DB Optimization

**Date:** 2025-08-09

## Contents
- **Slow SQL Profiler** (`app/observability/sql_profiler.py`)
  - Enable with `OBS_SQL_PROFILER=true` and (optional) `SLOW_SQL_MS=100`
  - Logs queries slower than threshold to `tenantra.sql` logger
- **TTL Cache Utility** (`app/cache/ttl.py`)
  - `TTLCache` class and `@ttl_cache(ttl_seconds=...)` decorator for read-heavy helpers
- **DB Indexes** (idempotent)
  - `users(username)` unique (if not already), `users(email)`
  - `audit_logs(user_id)`, `audit_logs(timestamp)`
  - `assets(tenant_id)`, `assets(last_seen)`

## Apply
```bash
unzip -o tenantra_patch_S17_Perf_DB.zip -d /path/to/tenantra-platform
cd /path/to/tenantra-platform/docker
docker compose up --build -d backend
docker compose exec -T backend alembic upgrade head
```

## Wire the SQL profiler (one-liner patch)
In `app/main.py` after app initialization:
```py
from app.database import engine
from app.observability.sql_profiler import init_sql_profiler
init_sql_profiler(engine)
```

## Validate
- Set `OBS_SQL_PROFILER=true` (and optionally `SLOW_SQL_MS=50`), restart backend
- Exercise API; check logs for `SLOW_SQL` lines
- Verify new indexes exist:
```sql
-- inside DB
\d users
\d audit_logs
\d assets
```

## Notes
- TTL cache is in-process; for multi-instance deployments, move critical caches to Redis.
