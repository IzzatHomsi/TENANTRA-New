"""Simple Redis TCP ping used by container health checks."""

from __future__ import annotations

import os
import socket
import sys
from pathlib import Path


def _load_password() -> bytes | None:
    candidate = os.environ.get("REDIS_PASSWORD_FILE", "/run/secrets/redis_password")
    try:
        data = Path(candidate).read_bytes()
    except FileNotFoundError:
        return None
    return data.strip() or None


def main() -> int:
    password = _load_password()
    try:
        with socket.create_connection(("redis", 6379), timeout=2) as sock:
            if password:
                sock.sendall(b"AUTH " + password + b"\r\n")
                reply = sock.recv(16)
                if not reply.startswith(b"+OK"):
                    return 1
            sock.sendall(b"PING\r\n")
            reply = sock.recv(8)
            return 0 if reply.startswith(b"+PONG") else 1
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())
