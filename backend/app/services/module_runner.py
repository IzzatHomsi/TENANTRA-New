"""Base module runner interfaces and helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from app.models.module import Module
from app.models.scan_module_result import ScanModuleResult


@dataclass
class ModuleContext:
    module: Module
    tenant_id: Optional[int]
    agent_id: Optional[int]
    user_id: Optional[int]
    parameters: Dict[str, Any]


@dataclass
class ModuleExecutionResult:
    status: str
    details: Dict[str, Any]
    recorded_at: datetime

    def to_record(self, *, module_id: int, tenant_id: Optional[int], agent_id: Optional[int]) -> ScanModuleResult:
        return ScanModuleResult(
            module_id=module_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            status=self.status,
            details=json.dumps(self.details, ensure_ascii=False),
            recorded_at=self.recorded_at,
        )


class ModuleRunner:
    """Abstract base class for module executors."""

    slug: str = ""
    categories: Tuple[str, ...] = ()
    parameter_schema: Dict[str, Any] = {}

    def run(self, context: ModuleContext) -> ModuleExecutionResult:
        raise NotImplementedError

    def get_parameter_schema(self) -> Dict[str, Any]:
        return self.parameter_schema


class ModuleExecutionError(Exception):
    """Raised when a module runner encounters a fatal error."""


def validate_status(status: str) -> str:
    allowed = {"success", "failed", "error", "skipped"}
    if status not in allowed:
        raise ValueError(f"Invalid status '{status}', expected one of {sorted(allowed)}")
    return status


def build_result(*, status: str, details: Dict[str, Any], recorded_at: Optional[datetime] = None) -> ModuleExecutionResult:
    return ModuleExecutionResult(
        status=validate_status(status),
        details=details,
        recorded_at=recorded_at or datetime.utcnow(),
    )
