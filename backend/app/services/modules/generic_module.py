"""Generic CSV-backed module runner."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from app.services.module_runner import ModuleContext, ModuleRunner, build_result


_FALLBACK_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "force_status": {
            "type": "string",
            "enum": ["success", "failed", "error", "skipped"],
            "description": "Override the runner outcome explicitly.",
        },
        "issues": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of issues detected by an external control plane.",
        },
        "notes": {
            "type": "string",
            "description": "Free-form notes to capture evidence or manual assessment context.",
        },
    },
    "additionalProperties": True,
}


class GenericCSVModuleRunner(ModuleRunner):
    """Fallback runner that synthesises results from module metadata."""

    slug = ""
    parameter_schema = _FALLBACK_SCHEMA

    def run(self, context: ModuleContext):  # type: ignore[override]
        params = context.parameters or {}
        status = _status_from_parameters(params)
        module = context.module

        details: Dict[str, Any] = {
            "module": module.name,
            "category": module.category,
            "phase": module.phase,
            "impact_level": module.impact_level,
            "purpose": module.purpose or module.description,
            "dependencies": module.dependencies,
            "preconditions": module.preconditions,
            "team": module.team,
            "target_application": module.application_target,
            "operating_systems": module.operating_systems,
            "compliance_mapping": module.compliance_mapping,
            "parameters": params,
            "generated_at": datetime.utcnow().isoformat(),
        }

        if status == "failed" and not details.get("issues"):
            issues = params.get("issues") or params.get("violations") or params.get("errors")
            if issues:
                details["issues"] = issues

        return build_result(status=status, details=details)


def _status_from_parameters(params: Dict[str, Any]) -> str:
    forced = params.get("force_status")
    if isinstance(forced, str):
        forced_lower = forced.lower()
        if forced_lower in {"success", "failed", "error", "skipped"}:
            return forced_lower
    if params.get("issues") or params.get("violations") or params.get("errors"):
        return "failed"
    return "success"
