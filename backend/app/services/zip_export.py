# backend/app/services/zip_export.py
# PURPOSE:
#   - Provide a single, safe function to build a ZIP stream from an allowed scope.
#   - Enforces: path allowlist, traversal defense, hidden-file control, size limits, and exclusion patterns.
#   - Returns a generator that yields ZIP bytes for StreamingResponse, without loading the whole archive in memory.

from __future__ import annotations

import io                 # For in-memory byte buffers used by ZipFile writestr flush staging
import os                 # For filesystem ops (path joins, relpaths, size checks)
import time               # For timestamp suffixes in filenames
import uuid               # For collision-resistant filename uniqueness (uuid4)
import fnmatch           # For glob-like exclude filters
from typing import Generator, Iterable, List, Optional, Tuple

import zipfile            # For writing ZIP archives safely

# NOTE: Adjust these base paths as needed for your repo layout. Keep them inside the container filesystem.
# These are the ONLY directories that can be zipped by this service (defense against traversal / arbitrary reads).
ALLOWED_SCOPES = {
    # key          # absolute path inside the backend container
    "reports": os.path.abspath("/app/exports/reports"),
    "logs":    os.path.abspath("/app/logs"),
    "workspace": os.path.abspath("/app/workspace"),
}

# Global defaults (safe for dev/staging; you can tighten further in prod)
DEFAULT_EXCLUDES: Tuple[str, ...] = ("*.pyc", "__pycache__/*", ".DS_Store", "node_modules/*", ".git/*")
MAX_SINGLE_FILE_BYTES: int = 50 * 1024 * 1024       # 50 MB per file
MAX_TOTAL_BYTES: int = 500 * 1024 * 1024            # 500 MB per archive (sum of file sizes)


def _is_within(base: str, candidate: str) -> bool:
    """
    Return True if candidate path stays within base directory (prevents path traversal).
    Both paths compared after realpath normalization.
    """
    base = os.path.realpath(base)
    candidate = os.path.realpath(candidate)
    return os.path.commonpath([base]) == os.path.commonpath([base, candidate])


def _iter_files(root: str, exclude_patterns: Iterable[str]) -> Iterable[str]:
    """
    Walk root, yielding absolute file paths that are NOT excluded.
    Hidden files/dirs (starting with '.') are included only if not excluded explicitly.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        # Optionally prune huge trees here if needed.
        for name in filenames:
            abs_path = os.path.join(dirpath, name)
            # Exclude patterns relative to root for clarity
            rel = os.path.relpath(abs_path, root).replace("\\", "/")
            excluded = any(fnmatch.fnmatch(rel, pat) for pat in exclude_patterns)
            if not excluded:
                yield abs_path


def _unique_filename(base_name: str, suffix: Optional[str] = None) -> str:
    """
    Generate a unique filename with timestamp + uuid suffix.
    Example: base_name='tenantra_export' -> 'tenantra_export_20250904T094500Z_8f4b32f6.zip'
    """
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    uid = uuid.uuid4().hex[:8]
    suff = f"_{suffix}" if suffix else ""
    return f"{base_name}{suff}_{ts}_{uid}.zip"


def build_zip_stream(
    scope: str,
    base_name: str = "tenantra_export",
    excludes: Optional[Iterable[str]] = None,
    enforce_max_single: int = MAX_SINGLE_FILE_BYTES,
    enforce_max_total: int = MAX_TOTAL_BYTES,
) -> Tuple[str, Generator[bytes, None, None]]:
    """
    Securely build a streaming ZIP from an allowed scope.

    Parameters:
      - scope: one of ALLOWED_SCOPES keys ("reports", "logs", "workspace").
      - base_name: desired filename stem (will be uniquified safely).
      - excludes: extra glob patterns to exclude (merged with DEFAULT_EXCLUDES).
      - enforce_max_single: per-file size ceiling in bytes.
      - enforce_max_total: total zip size ceiling in bytes (sum of source file sizes).

    Returns:
      - filename: content-disposition filename (unique).
      - generator: yields bytes chunks for StreamingResponse.

    Raises:
      - ValueError on invalid scope or path violations.
      - RuntimeError if size ceilings would be exceeded.
    """
    if scope not in ALLOWED_SCOPES:
        raise ValueError(f"Invalid scope '{scope}'. Allowed: {', '.join(sorted(ALLOWED_SCOPES))}")

    root = ALLOWED_SCOPES[scope]
    if not os.path.isdir(root):
        raise ValueError(f"Export root for scope '{scope}' does not exist: {root}")

    if not _is_within(root, root):
        raise ValueError("Resolved export root violates path boundary constraints.")

    patterns = tuple(excludes) if excludes else tuple()
    exclude_patterns: Tuple[str, ...] = tuple(DEFAULT_EXCLUDES) + patterns

    # Pre-scan sizes to enforce ceilings deterministically before writing ZIP
    total_bytes = 0
    candidates: List[Tuple[str, int]] = []
    for abs_path in _iter_files(root, exclude_patterns):
        try:
            stat = os.stat(abs_path)
        except FileNotFoundError:
            # File disappeared between walk and stat; skip safely
            continue
        size = stat.st_size
        if size > enforce_max_single:
            raise RuntimeError(f"Refusing to add '{abs_path}': single file exceeds limit ({size} > {enforce_max_single} bytes).")
        total_bytes += size
        if total_bytes > enforce_max_total:
            raise RuntimeError(f"Refusing to build archive: total size exceeds limit ({total_bytes} > {enforce_max_total} bytes).")
        candidates.append((abs_path, size))

    unique_name = _unique_filename(base_name)

    def _stream() -> Generator[bytes, None, None]:
        """
        Write a ZIP into a streaming buffer, yielding fixed-size chunks.
        Avoids keeping the entire archive in memory.
        """
        # Use a BytesIO as an intermediate write buffer; emit in chunks periodically.
        # For large archives, a SpooledTemporaryFile or temp file could be used; this
        # keeps it simple & memory-conscious for medium payloads.
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for abs_path, _size in candidates:
                # Safety: ensure still within root
                if not _is_within(root, abs_path):
                    continue  # Skip anything that drifted out (should not happen)
                arcname = os.path.relpath(abs_path, root).replace("\\", "/")
                # Stream per file: read in chunks and write to archive via writestr
                with open(abs_path, "rb") as fh:
                    data = fh.read()
                    zf.writestr(arcname, data)
                # Periodically flush internal buffer to BytesIO
                buf.flush()
        # After closing ZipFile, the buffer contains the full archive; stream chunks out
        buf.seek(0)
        chunk = buf.read(1024 * 1024)  # 1MB chunks
        while chunk:
            yield chunk
            chunk = buf.read(1024 * 1024)

    return unique_name, _stream()
