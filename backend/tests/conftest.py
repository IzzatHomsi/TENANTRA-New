import os
import sys
import time
import subprocess
from pathlib import Path

import pytest

# Ensure env is set as early as possible for modules importing DB config at import-time
os.environ.setdefault("DB_URL", "sqlite:///./test_api.db")
os.environ.setdefault("TENANTRA_TEST_BOOTSTRAP", "1")
os.environ.setdefault("TENANTRA_ENABLE_NOTIFICATIONS_WORKER", "0")
os.environ.setdefault("TENANTRA_ENABLE_MODULE_SCHEDULER", "0")


@pytest.fixture(scope="session", autouse=True)
def _ensure_api_server_and_env():
    """
    Session-scoped bootstrap that ensures:
    - Tests use a local SQLite DB instead of Postgres
    - The dev API server runs for requests-based tests
    """
    skip_server = os.environ.get("TENANTRA_TEST_SKIP_SERVER", "").lower() in {"1", "true", "yes"}
    if skip_server:
        yield
        return

    # Env already set at import-time; keep here to document intent

    # Start the dev server as a subprocess
    repo_root = Path(__file__).resolve().parents[2]
    dev_server = repo_root / "backend" / "dev_server.py"

    # On Windows, use the same Python executable
    proc = subprocess.Popen(
        [sys.executable, str(dev_server)],
        cwd=str(repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=os.environ.copy(),
    )

    # Wait for the server to accept connections
    import socket

    host, port = "127.0.0.1", 5000
    deadline = time.time() + 30
    last_err = None
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                break
        except OSError as e:
            last_err = e
            time.sleep(0.2)
    else:
        # Failed to start; ensure we clean up and raise
        try:
            proc.terminate()
        except Exception:
            pass
        raise RuntimeError(f"API server failed to start on {host}:{port}: {last_err}")

    yield

    # Teardown: stop the server
    try:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    except Exception:
        pass
