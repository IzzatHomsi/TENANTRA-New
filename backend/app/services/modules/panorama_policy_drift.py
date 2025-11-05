"""Panorama Policy Drift stub runner.

This is a Phase 3 network exposure component stub. It returns "skipped" unless
TENANTRA_ENABLE_PANORAMA_STUB is set true-ish. When enabled, it returns a simple
success payload with placeholders. Replace with real Panorama API integration later.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from app.services.module_runner import ModuleRunner, ModuleContext, build_result


class PanoramaPolicyDriftModule(ModuleRunner):
    slug = "panorama-policy-drift"
    categories = ("Networking Devices", "Network & Perimeter Security")
    parameter_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "panorama_url": {"type": "string"},
            "device_group": {"type": "string"},
        },
        "required": [],
    }

    def run(self, context: ModuleContext):  # type: ignore[override]
        enabled = os.getenv("TENANTRA_ENABLE_PANORAMA_STUB", "0").strip().lower() in {"1", "true", "yes", "on"}
        if not enabled:
            return build_result(status="skipped", details={
                "service": "panorama",
                "reason": "stub_disabled",
            })

        params = context.parameters or {}
        details: Dict[str, Any] = {
            "service": "panorama",
            "summary": {
                "device_group": params.get("device_group") or "default",
                "drift_items": 0,
            },
            "findings": [],
        }
        return build_result(status="success", details=details)

