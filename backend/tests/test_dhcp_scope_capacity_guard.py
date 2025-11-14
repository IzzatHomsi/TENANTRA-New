from app.models.module import Module, ModuleStatus
from app.services.module_runner import ModuleContext
from app.services.modules.dhcp_scope_capacity_guard import DHCPScopeCapacityGuard


def _make_context(parameters):
    module = Module(
        name="Networking — DHCP Scope Capacity Guard",
        external_id="dhcp-scope-capacity-guard",
        category="Network Devices",
        phase=5,
        status=ModuleStatus.ACTIVE,
        enabled=True,
    )
    return ModuleContext(module=module, tenant_id=None, agent_id=None, user_id=None, parameters=parameters)


def test_dhcp_scope_capacity_guard_success():
    runner = DHCPScopeCapacityGuard()
    context = _make_context(
        {
            "scopes": [
                {"name": "Branch-01", "total_leases": 512, "active_leases": 200, "reserved_leases": 10},
                {"name": "HQ-VoIP", "total_leases": 256, "active_leases": 90},
            ]
        }
    )
    result = runner.run(context)
    assert result.status == "success"
    details = result.details
    assert details["summary"]["scopes_evaluated"] == 2
    assert all(scope["status"] == "ok" for scope in details["scopes"])


def test_dhcp_scope_capacity_guard_threshold_breach():
    runner = DHCPScopeCapacityGuard()
    context = _make_context(
        {
            "warn_threshold_pct": 25,
            "critical_threshold_pct": 12,
            "source": {
                "type": "manual",
                "endpoint": "https://example.invalid/api",
                "password": "super-secret",
                "api_key": "should-not-echo",
            },
            "scopes": [
                {"name": "Remote-Site", "total_leases": 128, "active_leases": 120},
                {"name": "Lab-Network", "total_leases": 64, "active_leases": 50},
            ],
        }
    )
    result = runner.run(context)
    assert result.status == "failed"
    details = result.details
    assert any(f["scope"] == "Remote-Site" and f["severity"] == "critical" for f in details["findings"])
    parameters = details["parameters"]
    assert "password" not in parameters["source"]
    assert "api_key" not in parameters["source"]
