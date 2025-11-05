# rate_limit.py — simple per-user sliding-window limiter (in-memory)
import os, time, threading
from collections import deque
from fastapi import HTTPException, status

def _window_max():
    try:
        w = int(os.getenv("TENANTRA_EXPORT_RATE_WINDOW_SECONDS", "60"))
    except Exception:
        w = 60
    try:
        m = int(os.getenv("TENANTRA_EXPORT_RATE_MAX", "10"))
    except Exception:
        m = 10
    return w, m

_BUCKETS = {}
_LOCK = threading.Lock()

def rate_limit_export(user) -> None:
    """Raise HTTP 429 if user exceeds allowed requests within the window.
    Accepts any object with an integer-like 'id' attribute.
    """
    now = time.time()
    uid = getattr(user, "id", None)
    if uid is None:
        # If user id is unavailable, treat all as one bucket to be safe.
        uid = "anon"
    with _LOCK:
        q = _BUCKETS.get(uid)
        if q is None:
            q = deque()
            _BUCKETS[uid] = q
        window, maxreq = _window_max()
        while q and (now - q[0]) > window:
            q.popleft()
        if len(q) >= maxreq:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded ({maxreq}/{window}s)"
            )
        q.append(now)
