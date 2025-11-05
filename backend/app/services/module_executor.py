"""Centralised module execution helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.module import Module
from app.models.scan_module_result import ScanModuleResult
from app.services.module_registry import get_runner_for_module
from app.services.module_runner import ModuleContext, ModuleExecutionError


class ModuleRunnerNotFound(RuntimeError):
    """Raised when no runner implementation is available for a module."""


def execute_module(
    *,
    db: Session,
    module: Module,
    tenant_id: Optional[int],
    agent_id: Optional[int],
    user_id: Optional[int],
    parameters: Optional[Dict[str, Any]] = None,
) -> ScanModuleResult:
    runner = get_runner_for_module(module)
    if runner is None:
        raise ModuleRunnerNotFound(f"Module '{module.name}' does not have an associated runner")

    context = ModuleContext(
        module=module,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_id=user_id,
        parameters=parameters or {},
    )

    result = runner.run(context)
    record = result.to_record(
        module_id=module.id,
        tenant_id=tenant_id,
        agent_id=agent_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
