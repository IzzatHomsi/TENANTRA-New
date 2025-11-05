from __future__ import annotations

import os
import socket
from typing import Dict

from fastapi import FastAPI
from sqlalchemy import text

from app.database import SessionLocal


def _check_db() -> tuple[bool, str]:
    try:
        with SessionLocal() as s:
            s.execute(text("SELECT 1"))
        return True, "ok"
    except Exception as e:
        return False, f"db_error:{e.__class__.__name__}"


def _load_redis_password() -> bytes | None:
    candidates = [
        os.getenv("REDIS_PASSWORD_FILE") or "/run/secrets/redis_password",
    ]
    for c in candidates:
        try:
            with open(c, "rb") as fh:
                data = fh.read().strip()
                if data:
                    return data
        except Exception:
            # move on to next candidate path
            pass
    return None


def _check_redis() -> tuple[bool, str]:
    host = os.getenv("REDIS_HOST", "redis")
    port = int(os.getenv("REDIS_PORT", "6379"))
    pwd = _load_redis_password()
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            if pwd:
                sock.sendall(b"AUTH " + pwd + b"\r\n")
                reply = sock.recv(32)
                if not reply.startswith(b"+OK"):
                    return False, "redis_auth_failed"
            sock.sendall(b"PING\r\n")
            pong = sock.recv(16)
            if not pong.startswith(b"+PONG"):
                return False, "redis_ping_failed"
        return True, "ok"
    except Exception as e:
        return False, f"redis_error:{e.__class__.__name__}"


def build_app() -> FastAPI:
    app = FastAPI(title="Tenantra Worker Health", docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/worker/health")
    def worker_health() -> Dict[str, object]:
        ok_db, db_msg = _check_db()
        ok_rd, rd_msg = _check_redis()
        status = "ok" if ok_db and ok_rd else "degraded"
        return {"status": status, "db": ok_db, "db_msg": db_msg, "redis": ok_rd, "redis_msg": rd_msg}

    return app
