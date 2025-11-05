"""
SQL Profiler (lightweight)
- Logs queries slower than SLOW_SQL_MS (default 100ms)
- Enable with OBS_SQL_PROFILER=true
- Uses SQLAlchemy engine events; no query patching required
"""
import os
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

log = logging.getLogger("tenantra.sql")

SLOW_SQL_MS = int(os.getenv("SLOW_SQL_MS", "100"))
ENABLE = os.getenv("OBS_SQL_PROFILER", "false").lower() in ("1","true","yes")

def init_sql_profiler(engine: Engine) -> None:
    if not ENABLE:
        return

    _state = {}

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        _state[id(cursor)] = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        t0 = _state.pop(id(cursor), None)
        if t0 is None:
            return
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        if elapsed_ms >= SLOW_SQL_MS:
            # Trim excessive whitespace
            stmt = " ".join(str(statement).split())
            log.warning("SLOW_SQL %dms | %s | params=%s", elapsed_ms, stmt[:2000], parameters)
