"""
Simple in-process TTL cache for small config/data lookups.
NOT for large datasets or multi-instance coherence.
"""
import time
import threading
from typing import Any, Callable, Dict, Tuple

class TTLCache:
    def __init__(self, ttl_seconds: int = 60, maxsize: int = 1024):
        self.ttl = ttl_seconds
        self.maxsize = maxsize
        self.lock = threading.Lock()
        self.store: Dict[Any, Tuple[float, Any]] = {}

    def get(self, key: Any, loader: Callable[[], Any]):
        now = time.time()
        with self.lock:
            if key in self.store:
                ts, val = self.store[key]
                if now - ts < self.ttl:
                    return val
                else:
                    del self.store[key]
            val = loader()
            if len(self.store) >= self.maxsize:
                # FIFO-ish: pop an arbitrary item
                self.store.pop(next(iter(self.store)))
            self.store[key] = (now, val)
            return val

# Decorator
def ttl_cache(ttl_seconds: int = 60):
    def _wrap(func):
        cache = TTLCache(ttl_seconds=ttl_seconds)
        def _inner(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            return cache.get(key, lambda: func(*args, **kwargs))
        return _inner
    return _wrap
