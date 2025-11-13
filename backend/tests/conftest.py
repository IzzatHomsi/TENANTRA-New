import os
import secrets
import sys
import time
import subprocess
from pathlib import Path

import pytest

def _guess_repo_root() -> Path:
    start = Path(__file__).resolve().parent
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() or (candidate / "Makefile").exists():
            return candidate
    return start

REPO_ROOT = _guess_repo_root()

# Ensure env is set as early as possible for modules importing DB config at import-time
_TEST_DB_URL = os.getenv("TENANTRA_TEST_DB_URL", "sqlite:///./test_api.db")
if _TEST_DB_URL.startswith("sqlite") and ":memory:" not in _TEST_DB_URL:
    db_path = _TEST_DB_URL.replace("sqlite:///", "", 1)
    db_file = Path(db_path)
    if not db_file.is_absolute():
        db_file = (REPO_ROOT / db_file).resolve()
    try:
        db_file.unlink()
    except FileNotFoundError:
        pass
os.environ["DB_URL"] = _TEST_DB_URL
os.environ["DATABASE_URL"] = _TEST_DB_URL
os.environ["SQLALCHEMY_DATABASE_URI"] = _TEST_DB_URL
os.environ.setdefault("TENANTRA_TEST_BOOTSTRAP", "1")
os.environ.setdefault("TENANTRA_ENABLE_NOTIFICATIONS_WORKER", "0")
os.environ.setdefault("TENANTRA_ENABLE_MODULE_SCHEDULER", "0")
if "TENANTRA_TEST_ADMIN_PASSWORD" not in os.environ:
    os.environ["TENANTRA_TEST_ADMIN_PASSWORD"] = secrets.token_urlsafe(16)
os.environ["TENANTRA_ADMIN_PASSWORD"] = os.environ["TENANTRA_TEST_ADMIN_PASSWORD"]
os.environ["DEFAULT_ADMIN_PASSWORD"] = os.environ["TENANTRA_TEST_ADMIN_PASSWORD"]
if "TENANTRA_ENC_KEY" not in os.environ:
    os.environ["TENANTRA_ENC_KEY"] = secrets.token_hex(32)

# Ensure the lightweight bootstrap runs before tests import application modules
try:
    from app.bootstrap import bootstrap_test_data

    bootstrap_test_data()
except Exception:
    # Tests will fail visibly if bootstrap truly cannot run; swallow only to avoid import-time crashes.
    pass


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
    repo_root = REPO_ROOT
    dev_server = repo_root / "backend" / "dev_server.py"
    if not dev_server.exists():
        dev_server = repo_root / "dev_server.py"

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
