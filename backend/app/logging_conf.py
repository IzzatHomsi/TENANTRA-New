"""Minimal logging configuration for dev to ensure file + console output.

This module is auto-imported by app.main._init_logging() if present.
"""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path
import threading


_CTX = threading.local()


def set_request_context(**kwargs) -> None:
    """Set per-request logging context (safe no-op if not used in format)."""
    ctx = getattr(_CTX, "data", {})
    ctx.update({
        "req": kwargs.get("request_id"),
        "usr": kwargs.get("user_id"),
        "path": kwargs.get("path"),
        "method": kwargs.get("method"),
        "status": kwargs.get("status"),
    })
    _CTX.data = ctx


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        ctx = getattr(_CTX, "data", {}) or {}
        for key in ("req", "usr", "path", "method", "status"):
            if not hasattr(record, key):
                setattr(record, key, ctx.get(key))
        return True


def configure_logging() -> None:
    log_dir = Path(os.getenv("LOG_DIR", "/app/logs"))
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # fall back to current directory if /app/logs not writable
        log_dir = Path("./logs")
        log_dir.mkdir(parents=True, exist_ok=True)

    # Align with Admin Logs endpoint default path
    file_path = log_dir / "tenantra_backend.log"

    # Toggle file logging via env (off by default). Set TENANTRA_LOG_TO_FILE=1 to enable.
    log_to_file = str(os.getenv("TENANTRA_LOG_TO_FILE", "0")).strip().lower() in {"1", "true", "yes", "on"}

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "ctx": {"()": ContextFilter},
        },
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s | req=%(req)s usr=%(usr)s path=%(path)s",
            },
            "uvicorn_access": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s | req=%(req)s usr=%(usr)s path=%(path)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": os.getenv("LOG_LEVEL", "INFO").upper(),
                "formatter": "default",
                "stream": "ext://sys.stdout",
                "filters": ["ctx"],
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": os.getenv("LOG_LEVEL", "INFO").upper(),
                "formatter": "default",
                "filename": str(file_path),
                "maxBytes": 5 * 1024 * 1024,
                "backupCount": 3,
                "encoding": "utf-8",
                "filters": ["ctx"],
            },
        },
        "loggers": {
            "uvicorn": {"level": "INFO", "handlers": ["console"] + (["file"] if log_to_file else []), "propagate": False},
            "uvicorn.error": {"level": "INFO", "handlers": ["console"] + (["file"] if log_to_file else []), "propagate": False},
            "uvicorn.access": {"level": "INFO", "handlers": ["console"] + (["file"] if log_to_file else []), "propagate": False},
        },
        "root": {
            "level": os.getenv("LOG_LEVEL", "INFO").upper(),
            "handlers": ["console"] + (["file"] if log_to_file else []),
        },
    }

    logging.config.dictConfig(config)
    if log_to_file:
        logging.getLogger(__name__).info("Logging configured (console + file=%s)", file_path)
    else:
        logging.getLogger(__name__).info("Logging configured (console only; set TENANTRA_LOG_TO_FILE=1 to enable file logging)")
