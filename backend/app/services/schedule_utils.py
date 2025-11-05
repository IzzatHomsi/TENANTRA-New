"""Shared utilities for module scheduling."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional


def compute_next_run(cron_expr: str, *, reference: Optional[datetime] = None) -> datetime:
    """Very small cron helper supporting minute intervals (e.g. */15)."""
    reference = reference or datetime.utcnow()
    expr = (cron_expr or "").strip()
    if not expr:
        return reference + timedelta(hours=1)

    fields = expr.split()
    minute_field = fields[0] if fields else ""

    if minute_field.startswith("*/"):
        try:
            interval = int(minute_field[2:])
            if interval <= 0:
                raise ValueError
            return reference + timedelta(minutes=interval)
        except ValueError:
            return reference + timedelta(hours=1)

    # default: treat as hourly cron
    return reference + timedelta(hours=1)
