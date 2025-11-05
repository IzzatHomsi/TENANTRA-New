"""Category-level module runners mapping CSV modules to executable data."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List

from sqlalchemy import desc

from app.database import SessionLocal
from app.models.agent import Agent
from app.models.asset import Asset
from app.models.compliance_result import ComplianceResult
from app.models.network_visibility_result import NetworkVisibilityResult
from app.models.service_snapshot import ServiceSnapshot
from app.models.task_snapshot import TaskSnapshot
from app.models.user import User
from app.services.module_metadata import get_parameter_schema_for_category
from app.services.module_runner import ModuleContext, ModuleRunner, build_result

_ALLOWED_STATUSES = {"success", "failed", "error", "skipped"}


def _status_from_parameters(parameters: Dict[str, Any]) -> str:
    forced = parameters.get("force_status")
    if isinstance(forced, str):
        forced_lower = forced.lower()
        if forced_lower in _ALLOWED_STATUSES:
            return forced_lower
    if parameters.get("issues") or parameters.get("violations"):
        return "failed"
    return "success"


class CategoryModuleRunner(ModuleRunner):
    """Base class for category-driven modules backed by Tenantra data."""

    categories: Iterable[str] = ()

    def __init__(self) -> None:
        primary_category = next(iter(self.categories), None)
        if primary_category:
            schema = get_parameter_schema_for_category(primary_category)
            if schema:
                self.parameter_schema = schema

    def run(self, context: ModuleContext):  # type: ignore[override]
        parameters = context.parameters or {}
        status = _status_from_parameters(parameters)
        details = self._build_base_details(context, parameters, status)
        self.enrich_details(context, details)
        return build_result(status=status, details=details)

    def _build_base_details(
        self,
        context: ModuleContext,
        parameters: Dict[str, Any],
        status: str,
    ) -> Dict[str, Any]:
        module = context.module
        return {
            "module": module.name,
            "category": module.category,
            "purpose": module.purpose or module.description,
            "team": module.team,
            "target_application": module.application_target,
            "operating_systems": module.operating_systems,
            "status": status,
            "parameters": parameters,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def enrich_details(self, context: ModuleContext, details: Dict[str, Any]) -> None:
        return


class NetworkingDevicesModuleRunner(CategoryModuleRunner):
    categories = (
        "Networking Devices",
        "Network Devices",
        "Network Security",
        "Network & Perimeter Security",
    )

    def enrich_details(self, context: ModuleContext, details: Dict[str, Any]) -> None:  # type: ignore[override]
        params = context.parameters or {}
        session = SessionLocal()
        try:
            query = (
                session.query(NetworkVisibilityResult, Agent)
                .join(Agent, NetworkVisibilityResult.agent_id == Agent.id)
                .order_by(desc(NetworkVisibilityResult.recorded_at))
            )
            if context.agent_id:
                query = query.filter(NetworkVisibilityResult.agent_id == context.agent_id)
            if context.tenant_id:
                query = query.filter(Agent.tenant_id == context.tenant_id)
            rows = query.limit(25).all()
        finally:
            session.close()

        interfaces: List[Dict[str, Any]] = [
            {
                "agent": agent.name,
                "ip": agent.ip_address,
                "port": result.port,
                "service": result.service,
                "status": result.status,
                "recorded_at": result.recorded_at.isoformat() if result.recorded_at else None,
            }
            for result, agent in rows
        ]

        details.update(
            {
                "targets": params.get("targets") or [item["agent"] for item in interfaces],
                "interfaces": interfaces,
                "findings": params.get("issues") or [],
            }
        )


class ServerRolesModuleRunner(CategoryModuleRunner):
    categories = ("Server Roles",)

    def enrich_details(self, context: ModuleContext, details: Dict[str, Any]) -> None:  # type: ignore[override]
        params = context.parameters or {}
        session = SessionLocal()
        try:
            query = session.query(ServiceSnapshot)
            if context.agent_id:
                query = query.filter(ServiceSnapshot.agent_id == context.agent_id)
            if context.tenant_id:
                query = query.filter(ServiceSnapshot.tenant_id == context.tenant_id)
            snapshots = query.order_by(desc(ServiceSnapshot.collected_at)).limit(25).all()
        finally:
            session.close()

        details.update(
            {
                "role": params.get("role") or "generic_server",
                "baseline": params.get("baseline") or "hardened",
                "services": [snapshot.as_dict() for snapshot in snapshots],
                "deviations": params.get("issues") or [],
            }
        )


class LoggingObservabilityModuleRunner(CategoryModuleRunner):
    categories = ("Logging & Observability", "Microservices Observability", "End-to-End Monitoring")

    def enrich_details(self, context: ModuleContext, details: Dict[str, Any]) -> None:  # type: ignore[override]
        params = context.parameters or {}
        session = SessionLocal()
        try:
            query = session.query(Agent)
            if context.tenant_id:
                query = query.filter(Agent.tenant_id == context.tenant_id)
            agents = query.limit(12).all()
        finally:
            session.close()

        inventory = [
            {
                "agent": agent.name,
                "ip": agent.ip_address,
                "os": agent.os,
                "status": agent.status,
                "last_seen_at": agent.last_seen_at.isoformat() if agent.last_seen_at else None,
            }
            for agent in agents
        ]

        details.update(
            {
                "pipeline": params.get("pipeline") or "default",
                "coverage": params.get("coverage") or ["system", "application", "security"],
                "missing_sources": params.get("missing_sources") or [],
                "observability_targets": inventory,
            }
        )


class SecurityComplianceModuleRunner(CategoryModuleRunner):
    categories = (
        "Security & Compliance",
        "Continuous Compliance",
        "Compliance & Audit",
        "System Security Hygiene",
    )

    def enrich_details(self, context: ModuleContext, details: Dict[str, Any]) -> None:  # type: ignore[override]
        params = context.parameters or {}
        session = SessionLocal()
        try:
            query = session.query(ComplianceResult)
            if context.tenant_id:
                query = query.filter(ComplianceResult.tenant_id == context.tenant_id)
            if context.module.name:
                query = query.filter(ComplianceResult.module == context.module.name)
            results = query.order_by(desc(ComplianceResult.recorded_at)).limit(25).all()
        finally:
            session.close()

        history = [
            {
                "id": result.id,
                "status": result.status,
                "recorded_at": result.recorded_at.isoformat() if result.recorded_at else None,
                "details": result.details,
            }
            for result in results
        ]

        details.update(
            {
                "control_set": params.get("control_set") or context.module.name,
                "assessed_controls": params.get("assessed_controls", len(history)),
                "failing_controls": params.get("issues") or [],
                "evidence": history,
            }
        )


class InfrastructureInventoryModuleRunner(CategoryModuleRunner):
    categories = ("Infrastructure & Inventory", "Asset & Inventory Management")

    def enrich_details(self, context: ModuleContext, details: Dict[str, Any]) -> None:  # type: ignore[override]
        params = context.parameters or {}
        session = SessionLocal()
        try:
            query = session.query(Asset)
            if context.tenant_id:
                query = query.filter(Asset.tenant_id == context.tenant_id)
            assets = query.order_by(desc(Asset.updated_at)).limit(25).all()
        finally:
            session.close()

        inventory = [
            {
                "id": asset.id,
                "name": asset.name,
                "hostname": asset.hostname,
                "os": asset.os,
                "ip_address": asset.ip_address,
                "last_seen": asset.last_seen.isoformat() if asset.last_seen else None,
            }
            for asset in assets
        ]

        details.update(
            {
                "assets": inventory,
                "inventory_delta": params.get("inventory_delta") or {"added": 0, "removed": 0},
            }
        )


class UserAccountManagementModuleRunner(CategoryModuleRunner):
    categories = (
        "User & Account Management",
        "Identity & Access Management",
        "User & Access Control",
    )

    def enrich_details(self, context: ModuleContext, details: Dict[str, Any]) -> None:  # type: ignore[override]
        params = context.parameters or {}
        session = SessionLocal()
        try:
            query = session.query(User)
            if context.tenant_id:
                query = query.filter(User.tenant_id == context.tenant_id)
            users = query.limit(50).all()
        finally:
            session.close()

        orphan_accounts = [user.username for user in users if not user.email]
        elevated_accounts = [
            user.username
            for user in users
            if (getattr(user, "role", "") or "").lower() in {"admin", "super_admin"}
        ]

        details.update(
            {
                "orphan_accounts": params.get("orphan_accounts") or orphan_accounts,
                "elevated_accounts": params.get("elevated_accounts") or elevated_accounts,
                "policy_violations": params.get("violations") or [],
            }
        )


class ITProcessAutomationModuleRunner(CategoryModuleRunner):
    categories = ("IT Process Automation", "Automation & Orchestration")

    def enrich_details(self, context: ModuleContext, details: Dict[str, Any]) -> None:  # type: ignore[override]
        params = context.parameters or {}
        session = SessionLocal()
        try:
            query = session.query(TaskSnapshot)
            if context.agent_id:
                query = query.filter(TaskSnapshot.agent_id == context.agent_id)
            if context.tenant_id:
                query = query.filter(TaskSnapshot.tenant_id == context.tenant_id)
            tasks = query.order_by(desc(TaskSnapshot.collected_at)).limit(25).all()
        finally:
            session.close()

        details.update(
            {
                "workflows": [task.as_dict() for task in tasks] or params.get("workflows") or [],
                "completed": params.get("completed", len(tasks)),
                "failed": params.get("failed", 0),
                "tickets_created": params.get("tickets_created", 0),
            }
        )

