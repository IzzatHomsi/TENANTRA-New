# test_rate_limit.py — verifies per-user sliding window limiter
import time
from types import SimpleNamespace
from fastapi import HTTPException
from app.core.rate_limit import rate_limit_export

def test_rate_limit(monkeypatch):
    # Config: allow max 2 requests per 1 second for test speed
    monkeypatch.setenv("TENANTRA_EXPORT_RATE_WINDOW_SECONDS", "1")
    monkeypatch.setenv("TENANTRA_EXPORT_RATE_MAX", "2")
    user = SimpleNamespace(id="U1")
    rate_limit_export(user)  # 1
    rate_limit_export(user)  # 2
    try:
        rate_limit_export(user)  # 3 -> should 429
        assert False, "Expected 429"
    except Exception as e:
        assert isinstance(e, HTTPException) and e.status_code == 429
    # After 1s window, should allow again
    time.sleep(1.1)
    rate_limit_export(user)
