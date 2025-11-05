"""Shared metadata for scan module parameter schemas derived from CSV categories."""

from __future__ import annotations

from typing import Any, Dict, Optional

_CATEGORY_PARAMETER_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "networking devices": {
        "type": "object",
        "properties": {
            "targets": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of network device hostnames or IPs to evaluate.",
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Known misconfigurations to flag as failures.",
            },
            "force_status": {
                "type": "string",
                "enum": ["success", "failed", "error", "skipped"],
                "description": "Override the execution status returned by the runner.",
            },
        },
        "additionalProperties": True,
    },
    "server roles": {
        "type": "object",
        "properties": {
            "role": {"type": "string", "description": "Server role identifier (e.g., web, sql)."},
            "baseline": {"type": "string", "description": "Expected baseline template."},
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Configuration drift notes to mark as failures.",
            },
            "force_status": {
                "type": "string",
                "enum": ["success", "failed", "error", "skipped"],
            },
        },
        "additionalProperties": True,
    },
    "logging & observability": {
        "type": "object",
        "properties": {
            "pipeline": {"type": "string", "description": "Pipeline identifier to validate."},
            "coverage": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Expected telemetry coverage areas.",
            },
            "missing_sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Sources absent from the pipeline.",
            },
            "force_status": {
                "type": "string",
                "enum": ["success", "failed", "error", "skipped"],
            },
        },
        "additionalProperties": True,
    },
    "security & compliance": {
        "type": "object",
        "properties": {
            "control_set": {"type": "string", "description": "Set of controls to evaluate."},
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Failing controls or evidence gaps.",
            },
            "assessed_controls": {"type": "integer", "minimum": 0},
            "force_status": {
                "type": "string",
                "enum": ["success", "failed", "error", "skipped"],
            },
        },
        "additionalProperties": True,
    },
    "infrastructure & inventory": {
        "type": "object",
        "properties": {
            "discovered_assets": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Collection of assets identified in the scan.",
            },
            "inventory_delta": {
                "type": "object",
                "description": "Delta of assets added or removed since last run.",
            },
            "force_status": {
                "type": "string",
                "enum": ["success", "failed", "error", "skipped"],
            },
        },
        "additionalProperties": True,
    },
    "user & account management": {
        "type": "object",
        "properties": {
            "orphan_accounts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Accounts lacking owners.",
            },
            "elevated_accounts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Privileged accounts to review.",
            },
            "violations": {
                "type": "array",
                "items": {"type": "string"},
            },
            "force_status": {
                "type": "string",
                "enum": ["success", "failed", "error", "skipped"],
            },
        },
        "additionalProperties": True,
    },
    "it process automation": {
        "type": "object",
        "properties": {
            "workflows": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Automation workflows executed.",
            },
            "completed": {"type": "integer", "minimum": 0},
            "failed": {"type": "integer", "minimum": 0},
            "tickets_created": {"type": "integer", "minimum": 0},
            "force_status": {
                "type": "string",
                "enum": ["success", "failed", "error", "skipped"],
            },
        },
        "additionalProperties": True,
    },
}

# Map aliases to canonical schemas
_ALIASES = {
    "network devices": "networking devices",
    "network security": "networking devices",
    "network & perimeter security": "networking devices",
    "identity & access management": "user & account management",
    "user & access control": "user & account management",
    "automation & orchestration": "it process automation",
    "continuous compliance": "security & compliance",
    "compliance & audit": "security & compliance",
    "system security hygiene": "security & compliance",
    "asset & inventory management": "infrastructure & inventory",
    "microservices observability": "logging & observability",
    "end-to-end monitoring": "logging & observability",
}


for alias, target in _ALIASES.items():
    if alias not in _CATEGORY_PARAMETER_SCHEMAS:
        _CATEGORY_PARAMETER_SCHEMAS[alias] = _CATEGORY_PARAMETER_SCHEMAS[target]


def get_parameter_schema_for_category(category: Optional[str]) -> Dict[str, Any]:
    if not category:
        return {}
    key = category.strip().lower()
    return _CATEGORY_PARAMETER_SCHEMAS.get(key, {})

