# backend/app/core/zipper.py
# Secure, tenant-scoped ZIP builder with optional DB CSV export.

import os
from collections.abc import Iterable, Sequence
import zipfile

from app.db import get_db_session

try:
    from app.models.asset import Asset  # optional; export assets.csv if present
except Exception:
    Asset = None  # type: ignore

def _is_within_base(base: str, target: str) -> bool:
    base_real = os.path.realpath(base)
    target_real = os.path.realpath(target)
    try:
        return os.path.commonpath([target_real, base_real]) == base_real
    except ValueError:
        # Raised when paths are on different drives on Windows.
        return False

def _safe_add_file(zf: zipfile.ZipFile, base_dir: str, abs_path: str, arc_prefix: str = "") -> None:
    if not _is_within_base(base_dir, abs_path):
        return
    arcname = os.path.join(arc_prefix, os.path.relpath(abs_path, base_dir)).replace("\\", "/")
    zf.write(abs_path, arcname=arcname)


def _normalize_base(base: str) -> str:
    return os.path.realpath(base)


def sanitize_and_validate_paths(paths: Iterable[str], base_root: str) -> tuple[list[str], list[tuple[str, str]]]:
    """Validate a list of relative paths under ``base_root``.

    Returns a tuple of ``(valid_paths, rejected)`` where ``valid_paths`` is a list of absolute
    paths and ``rejected`` contains the rejected user inputs with a short explanation.
    """

    valid: list[str] = []
    rejected: list[tuple[str, str]] = []
    seen: set[str] = set()

    base_real = _normalize_base(base_root)

    for raw in paths:
        if not raw:
            rejected.append((raw, "empty path"))
            continue

        candidate = raw if os.path.isabs(raw) else os.path.join(base_real, raw)
        candidate_real = os.path.realpath(candidate)

        if not _is_within_base(base_real, candidate_real):
            rejected.append((raw, "outside allowed root"))
            continue

        if not os.path.exists(candidate_real):
            rejected.append((raw, "not found"))
            continue

        if candidate_real in seen:
            # Skip duplicates silently.
            continue

        seen.add(candidate_real)
        valid.append(candidate_real)

    return valid, rejected


def _match_base(path: str, base_roots: Sequence[str]) -> str | None:
    for base in base_roots:
        if _is_within_base(base, path):
            return base
    return None


def create_zip_from_paths(
    output_zip: str, paths: Sequence[str], base_root: str, arc_prefix: str = ""
) -> None:
    out_dir = os.path.dirname(output_zip) or "."
    os.makedirs(out_dir, exist_ok=True)
    base_real = _normalize_base(base_root)

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for abs_path in paths:
            abs_real = os.path.realpath(abs_path)
            if not _is_within_base(base_real, abs_real):
                continue

            if os.path.isdir(abs_real):
                for root, _, files in os.walk(abs_real):
                    for name in files:
                        _safe_add_file(zf, base_real, os.path.join(root, name), arc_prefix=arc_prefix)
            else:
                _safe_add_file(zf, base_real, abs_real, arc_prefix=arc_prefix)


def sanitize_and_validate_paths_multi(
    paths: Iterable[str], base_roots: Sequence[str]
) -> tuple[list[str], list[tuple[str, str]], list[str]]:
    """Validate paths against multiple allowed roots.

    Returns ``(valid_paths, rejected, used_roots)``. ``valid_paths`` is a list of absolute paths,
    ``rejected`` mirrors :func:`sanitize_and_validate_paths`, and ``used_roots`` contains the
    subset of ``base_roots`` that provided at least one valid file.
    """

    valid: list[str] = []
    rejected: list[tuple[str, str]] = []
    used_roots: set[str] = set()
    seen: set[str] = set()

    normalized_roots = [_normalize_base(b) for b in base_roots if b]

    for raw in paths:
        if not raw:
            rejected.append((raw, "empty path"))
            continue

        candidate_paths = []
        if os.path.isabs(raw):
            candidate_paths.append(os.path.realpath(raw))
        else:
            for base in normalized_roots:
                candidate_paths.append(os.path.realpath(os.path.join(base, raw)))

        added = False
        for candidate_real in candidate_paths:
            base_match = _match_base(candidate_real, normalized_roots)
            if base_match is None:
                continue
            if not os.path.exists(candidate_real):
                continue
            if candidate_real in seen:
                added = True
                used_roots.add(base_match)
                break

            valid.append(candidate_real)
            seen.add(candidate_real)
            used_roots.add(base_match)
            added = True
            break

        if not added:
            rejected.append((raw, "not found in allowed roots"))

    return valid, rejected, sorted(used_roots)


def create_zip_from_paths_multi(
    output_zip: str, paths: Sequence[str], base_roots: Sequence[str], arc_prefix: str = ""
) -> None:
    out_dir = os.path.dirname(output_zip) or "."
    os.makedirs(out_dir, exist_ok=True)
    normalized_roots = [_normalize_base(b) for b in base_roots if b]

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for abs_path in paths:
            abs_real = os.path.realpath(abs_path)
            base_match = _match_base(abs_real, normalized_roots)
            if base_match is None:
                continue

            if os.path.isdir(abs_real):
                for root, _, files in os.walk(abs_real):
                    for name in files:
                        _safe_add_file(
                            zf,
                            base_match,
                            os.path.join(root, name),
                            arc_prefix=arc_prefix,
                        )
            else:
                _safe_add_file(zf, base_match, abs_real, arc_prefix=arc_prefix)

def build_tenant_export_zip(tenant_id: int, output_zip: str) -> None:
    base_collect_dir = f"/app/data/tenants/{tenant_id}"
    os.makedirs(os.path.dirname(output_zip), exist_ok=True)

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # manifest
        zf.writestr("MANIFEST.txt", f"tenant_id={tenant_id}\n")

        # safe file collection
        if os.path.isdir(base_collect_dir):
            for root, _, files in os.walk(base_collect_dir):
                for name in files:
                    _safe_add_file(zf, base_collect_dir, os.path.join(root, name), arc_prefix="tenant_data")

        # optional DB snapshot
        if Asset is not None:
            with get_db_session() as db:
                rows = (
                    db.query(Asset)
                    .filter(Asset.tenant_id == tenant_id)
                    .limit(10000)
                    .all()
                )
                lines = ["id,name,hostname,ip\n"]
                for a in rows:
                    lines.append(f"{a.id},{a.name},{a.hostname},{a.ip}\n")
                zf.writestr("assets.csv", "".join(lines))
