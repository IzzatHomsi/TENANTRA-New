"""Phase 2 – AWS IAM Baseline runner (scaffold).

This runner does not call AWS APIs; instead, it evaluates parameters passed in the
module run payload. This keeps CI lightweight and deterministic while we build out
live integrations later.

Slug: aws-iam-baseline
Category: Identity & Access Scanning
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from app.services.module_runner import ModuleRunner, ModuleContext, build_result


class AWSIAMBaselineModule(ModuleRunner):
    slug = "aws-iam-baseline"
    categories = ("Identity & Access Scanning",)
    parameter_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "users": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "mfa_enabled": {"type": "boolean"},
                        "access_keys": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "age_days": {"type": "integer"},
                                    "active": {"type": "boolean"},
                                },
                                "required": ["age_days", "active"],
                            },
                            "default": [],
                        },
                    },
                    "required": ["username", "mfa_enabled"],
                },
                "default": [],
            },
            "max_key_age_days": {"type": "integer", "default": 90},
            "require_mfa": {"type": "boolean", "default": True},
        },
        "required": [],
    }

    def run(self, context: ModuleContext):  # type: ignore[override]
        # Optional live check via AWS APIs (kept off in CI). Enable with TENANTRA_ENABLE_AWS_LIVE=true
        if os.getenv("TENANTRA_ENABLE_AWS_LIVE", "0").strip().lower() in {"1", "true", "yes", "on"}:
            live = self._try_live_scan()
            if live is not None:
                return live

        params = context.parameters or {}
        users: List[Dict[str, Any]] = params.get("users", [])
        max_age: int = int(params.get("max_key_age_days", 90))
        require_mfa: bool = bool(params.get("require_mfa", True))
        return self._evaluate(users, max_age, require_mfa)

    # --- helpers ---
    def _try_live_scan(self):
        try:
            import boto3  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dep
            return build_result(status="skipped", details={
                "service": "aws-iam",
                "reason": "boto3_missing",
                "error": str(exc),
            })

        try:
            iam = boto3.client("iam")
            users: List[Dict[str, Any]] = []
            paginator = iam.get_paginator("list_users")
            for page in paginator.paginate():
                for u in page.get("Users", []):
                    username = u.get("UserName")
                    # MFA devices for user
                    mfa_resp = iam.list_mfa_devices(UserName=username)
                    mfa_enabled = len(mfa_resp.get("MFADevices", [])) > 0
                    # access keys
                    keys_info: List[Dict[str, Any]] = []
                    key_resp = iam.list_access_keys(UserName=username)
                    for meta in key_resp.get("AccessKeyMetadata", []):
                        create_dt = meta.get("CreateDate")
                        if isinstance(create_dt, datetime):
                            age_days = int((datetime.now(timezone.utc) - create_dt).days)
                        else:
                            age_days = 0
                        active = (meta.get("Status") == "Active")
                        keys_info.append({"age_days": age_days, "active": active})

                    users.append({"username": username, "mfa_enabled": mfa_enabled, "access_keys": keys_info})

            # Evaluate with synthesized parameters
            return self._evaluate(
                users=users,
                max_age=int(os.getenv("TENANTRA_AWS_MAX_KEY_AGE", "90")),
                require_mfa=os.getenv("TENANTRA_AWS_REQUIRE_MFA", "true").lower() in {"1","true","yes","on"},
            )
        except Exception as exc:  # pragma: no cover - safety
            return build_result(status="skipped", details={
                "service": "aws-iam",
                "reason": "live_unavailable",
                "error": str(exc)[:500],
            })

    def _evaluate(self, users: List[Dict[str, Any]], max_age: int, require_mfa: bool):
        noncompliant: List[Dict[str, Any]] = []
        mfa_missing: List[str] = []
        old_keys: List[Tuple[str, int]] = []

        for u in users:
            uname = str(u.get("username", "?"))
            mfa_enabled = bool(u.get("mfa_enabled", False))
            if require_mfa and not mfa_enabled:
                mfa_missing.append(uname)
            for key in (u.get("access_keys") or []):
                age = int(key.get("age_days", 0))
                active = bool(key.get("active", True))
                if active and age > max_age:
                    old_keys.append((uname, age))

        if mfa_missing or old_keys:
            for uname in mfa_missing:
                noncompliant.append({"user": uname, "issue": "mfa_missing"})
            for uname, age in old_keys:
                noncompliant.append({"user": uname, "issue": "access_key_too_old", "age_days": age})

        status = "success" if not noncompliant else "failed"
        details: Dict[str, Any] = {
            "service": "aws-iam",
            "summary": {
                "users_checked": len(users),
                "mfa_missing": len(mfa_missing),
                "old_keys": len(old_keys),
                "max_key_age_days": max_age,
                "require_mfa": require_mfa,
            },
            "findings": noncompliant,
        }

        return build_result(status=status, details=details)
