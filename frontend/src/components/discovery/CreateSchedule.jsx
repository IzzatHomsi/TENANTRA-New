import React, { useState, useEffect } from "react";
import { getApiBase } from "../../utils/apiBase";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";
import { useUIStore } from "../../store/uiStore";
import { fetchTenants } from "../../api/tenants";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

export default function CreateSchedule({ isAdmin }) {
  const [cron, setCron] = useState("*/30 * * * *");
  const [schedMsg, setSchedMsg] = useState("");
  const [error, setError] = useState("");
  const [agents, setAgents] = useState([]);
  const [tenantId, setTenantId] = useState("");
  const [agentId, setAgentId] = useState("");
  const [targets, setTargets] = useState([]);
  const { tenants } = useUIStore();

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  useEffect(() => {
    (async () => {
      if (!isAdmin) return;
      if (tenants.length > 0) return;
      try {
        await fetchTenants(token);
      } catch {}
    })();
  }, [isAdmin, token, tenants.length]);

  useEffect(() => {
    (async () => {
      if (!isAdmin) return;
      try {
        const qs = tenantId ? `?tenant_id=${tenantId}` : "";
        const res = await fetch(`${API_BASE}/admin/agents${qs}`, { headers: authHeaders(token) });
        if (res.ok) {
          setAgents(await res.json());
        }
      } catch {
        setAgents([]);
      }
    })();
  }, [isAdmin, token, tenantId]);

  const createSchedule = async () => {
    setSchedMsg("");
    setError("");
    if (!targets.length) {
      setError("Provide a CIDR or at least one host.");
      return;
    }
    try {
      let modules = await fetch(`${API_BASE}/modules/`, { headers: authHeaders(token) }).then(res => res.json());
      let mod = (modules || []).find(m => (m.external_id||'').toLowerCase() === 'port-scan' || /port\s*scan/i.test(m.name||''));
      if (!mod) {
        try {
          await fetch(`${API_BASE}/admin/modules/create-port-scan`, { method: "POST", headers: authHeaders(token) });
        } catch {}
        modules = await fetch(`${API_BASE}/modules/`, { headers: authHeaders(token) }).then(res => res.json());
        mod = (modules || []).find(m => (m.external_id||'').toLowerCase() === 'port-scan' || /port\s*scan/i.test(m.name||''));
      }
      if (!mod) {
        setError("Port Scan module not available. Ask an admin to seed modules.");
        return;
      }
      const payload = { module_id: mod.id, cron_expr: cron.trim() || "*/30 * * * *", parameters: { targets } };
      if (isAdmin && tenantId) {
        payload.tenant_id = Number(tenantId);
      }
      if (agentId) {
        const parsed = Number(agentId);
        if (!isNaN(parsed) && parsed > 0) {
          payload.agent_id = parsed;
        }
      }
      await fetch(`${API_BASE}/schedules`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
      setSchedMsg("Schedule created. View under Module Catalog → Schedules or Scan Orchestration.");
      setTimeout(() => setSchedMsg(""), 2600);
    } catch (e) {
      setError(e?.message || "Failed to create schedule");
    }
  };

  return (
    <Card>
      <h2 className="mb-4 text-xl font-bold text-gray-900">Create Recurring Schedule</h2>
      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}
      {schedMsg && <div className="mb-4 rounded-md bg-green-100 p-4 text-green-700">{schedMsg}</div>}
      <div className="space-y-4">
        {isAdmin && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Tenant (admin)</label>
              <select
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              >
                <option value="">Current tenant</option>
                {tenants.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Agent (optional)</label>
              <select
                value={agentId}
                onChange={(e) => setAgentId(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              >
                <option value="">Unassigned</option>
                {agents.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name} (#{a.id})
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-gray-700">Cron expression</label>
          <input
            value={cron}
            onChange={(e) => setCron(e.target.value)}
            placeholder="*/30 * * * *"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          />
        </div>
        <Button onClick={createSchedule}>Save Schedule</Button>
      </div>
    </Card>
  );
}
