"""Registry mapping module slugs/categories to runner implementations."""

from __future__ import annotations

from typing import Dict, Optional

from app.models.module import Module
from app.services.module_runner import ModuleRunner

# Import implementations so they register below
from app.services.modules.cis_benchmark import CISBenchmarkModule
from app.services.modules.pci_dss_check import PCIDSSCheckModule
from app.services.modules.category_runners import (
    InfrastructureInventoryModuleRunner,
    ITProcessAutomationModuleRunner,
    LoggingObservabilityModuleRunner,
    NetworkingDevicesModuleRunner,
    SecurityComplianceModuleRunner,
    ServerRolesModuleRunner,
    UserAccountManagementModuleRunner,
)
from app.services.modules.aws_iam_baseline import AWSIAMBaselineModule
from app.services.modules.dhcp_scope_capacity_guard import DHCPScopeCapacityGuard
from app.services.modules.generic_module import GenericCSVModuleRunner
from app.services.modules.port_scan import PortScanModule
from app.services.modules.panorama_policy_drift import PanoramaPolicyDriftModule

_slug_runners: Dict[str, ModuleRunner] = {}
_category_runners: Dict[str, ModuleRunner] = {}
_generic_runner = GenericCSVModuleRunner()


def _register(runner: ModuleRunner) -> None:
    slug = (runner.slug or "").strip().lower()
    if slug:
        _slug_runners[slug] = runner
    categories = getattr(runner, "categories", ()) or ()
    for category in categories:
        key = (category or "").strip().lower()
        if key:
            _category_runners[key] = runner


# Explicit module-slug runners
_register(CISBenchmarkModule())
_register(PCIDSSCheckModule())
_register(AWSIAMBaselineModule())
_register(PanoramaPolicyDriftModule())
_register(DHCPScopeCapacityGuard())

# Category-wide runners (share behaviour across many CSV modules)
for runner in (
    NetworkingDevicesModuleRunner(),
    ServerRolesModuleRunner(),
    LoggingObservabilityModuleRunner(),
    PortScanModule(),
    SecurityComplianceModuleRunner(),
    InfrastructureInventoryModuleRunner(),
    UserAccountManagementModuleRunner(),
    ITProcessAutomationModuleRunner(),
):
    _register(runner)


def get_runner_for_module(module: Module) -> Optional[ModuleRunner]:
    key = (module.external_id or module.name or "").strip().lower()
    if key in _slug_runners:
        return _slug_runners[key]

    name_key = (module.name or "").strip().lower()
    if name_key in _slug_runners:
        return _slug_runners[name_key]

    category_key = (module.category or "").strip().lower()
    if category_key and category_key in _category_runners:
        return _category_runners[category_key]

    return _generic_runner


def list_registered_modules() -> Dict[str, ModuleRunner]:
    return dict(_slug_runners)


def get_parameter_schema_for_module(module: Module) -> Dict[str, object]:
    runner = get_runner_for_module(module)
    if runner:
        return runner.get_parameter_schema()
    return {}
