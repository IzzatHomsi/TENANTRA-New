"""Seed demo telemetry data for Tenantra module runners."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.agent import Agent
from app.models.asset import Asset
from app.models.compliance_result import ComplianceResult
from app.models.network_visibility_result import NetworkVisibilityResult
from app.models.service_snapshot import ServiceSnapshot
from app.models.task_snapshot import TaskSnapshot


def _ensure_agent(session, name: str, tenant_id: int) -> Agent:
    agent = (
        session.query(Agent)
        .filter(Agent.name == name, Agent.tenant_id == tenant_id)
        .first()
    )
    if agent:
        return agent

    agent = Agent(
        name=name,
        tenant_id=tenant_id,
        token=f"demo-{name}",
        ip_address="10.0.0.10",
        os="linux",
        status="active",
        last_seen_at=datetime.utcnow(),
    )
    session.add(agent)
    session.flush()
    return agent


def seed_network(session, agent: Agent) -> None:
    if (
        session.query(NetworkVisibilityResult)
        .filter(NetworkVisibilityResult.agent_id == agent.id)
        .count()
    ):
        return

    now = datetime.utcnow()
    rows = [
        NetworkVisibilityResult(
            agent_id=agent.id,
            port=22,
            service="ssh",
            status="open",
            recorded_at=now - timedelta(minutes=5),
        ),
        NetworkVisibilityResult(
            agent_id=agent.id,
            port=443,
            service="https",
            status="open",
            recorded_at=now - timedelta(minutes=3),
        ),
        NetworkVisibilityResult(
            agent_id=agent.id,
            port=3389,
            service="rdp",
            status="closed",
            recorded_at=now - timedelta(minutes=2),
        ),
    ]
    session.add_all(rows)


def seed_services(session, agent: Agent) -> None:
    if (
        session.query(ServiceSnapshot)
        .filter(ServiceSnapshot.agent_id == agent.id)
        .count()
    ):
        return

    now = datetime.utcnow()
    services = [
        ServiceSnapshot(
            tenant_id=agent.tenant_id,
            agent_id=agent.id,
            name="nginx",
            display_name="nginx",
            status="running",
            start_mode="auto",
            run_account="root",
            binary_path="/usr/sbin/nginx",
            hash="123abc",
            collected_at=now,
        ),
        ServiceSnapshot(
            tenant_id=agent.tenant_id,
            agent_id=agent.id,
            name="sshd",
            display_name="OpenSSH",
            status="running",
            start_mode="auto",
            run_account="root",
            binary_path="/usr/sbin/sshd",
            hash="456def",
            collected_at=now,
        ),
    ]
    session.add_all(services)


def seed_tasks(session, agent: Agent) -> None:
    if (
        session.query(TaskSnapshot)
        .filter(TaskSnapshot.agent_id == agent.id)
        .count()
    ):
        return

    now = datetime.utcnow()
    tasks = [
        TaskSnapshot(
            tenant_id=agent.tenant_id,
            agent_id=agent.id,
            name="nightly_backup",
            task_type="cron",
            schedule="0 2 * * *",
            command="/usr/local/bin/backup.sh",
            last_run_time=now - timedelta(days=1),
            next_run_time=now + timedelta(hours=10),
            status="success",
            collected_at=now,
        ),
        TaskSnapshot(
            tenant_id=agent.tenant_id,
            agent_id=agent.id,
            name="log_rotate",
            task_type="cron",
            schedule="0 */6 * * *",
            command="/usr/sbin/logrotate",
            last_run_time=now - timedelta(hours=4),
            next_run_time=now + timedelta(hours=2),
            status="success",
            collected_at=now,
        ),
    ]
    session.add_all(tasks)


def seed_assets(session, tenant_id: int) -> None:
    if session.query(Asset).filter(Asset.tenant_id == tenant_id).count():
        return

    now = datetime.utcnow()
    assets = [
        Asset(
            tenant_id=tenant_id,
            name="app-server-01",
            description="Web front-end",
            ip_address="10.0.0.11",
            os="Ubuntu 22.04",
            hostname="app-server-01",
            last_seen=now,
        ),
        Asset(
            tenant_id=tenant_id,
            name="db-core-01",
            description="Primary database",
            ip_address="10.0.0.12",
            os="PostgreSQL Appliance",
            hostname="db-core-01",
            last_seen=now,
        ),
    ]
    session.add_all(assets)


def seed_compliance(session, tenant_id: int) -> None:
    if session.query(ComplianceResult).filter(ComplianceResult.tenant_id == tenant_id).count():
        return

    now = datetime.utcnow()
    results = [
        ComplianceResult(
            tenant_id=tenant_id,
            module="pci_dss_check",
            status="success",
            recorded_at=now - timedelta(hours=6),
            details="All cardholder data stores are encrypted.",
        ),
        ComplianceResult(
            tenant_id=tenant_id,
            module="cis_benchmark",
            status="failed",
            recorded_at=now - timedelta(hours=2),
            details="Control 1.1.1 failed on app-server-01",
        ),
    ]
    session.add_all(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo telemetry data for module runners")
    parser.add_argument("--tenant-id", type=int, default=1, help="Tenant ID to populate")
    parser.add_argument("--agent-name", type=str, default="tenant-agent-1", help="Agent name for seeded data")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        agent = _ensure_agent(session, args.agent_name, args.tenant_id)
        seed_network(session, agent)
        seed_services(session, agent)
        seed_tasks(session, agent)
        seed_assets(session, args.tenant_id)
        seed_compliance(session, args.tenant_id)
        session.commit()
        print("Seeded demo telemetry for tenant", args.tenant_id)
    finally:
        session.close()


if __name__ == "__main__":
    main()
