import React, { useState, useEffect } from "react";
import Button from "../ui/Button.jsx";
import Table from "../ui/Table.jsx";
import { getApiBase } from "../../utils/apiBase";
import { useUIStore } from "../../store/uiStore";
import { fetchTenants } from "../../api/tenants";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const formatDate = (value) => {
  if (!value) return "?";
  return new Date(value).toLocaleString();
};

export default function ScheduleModule({ module, isAdmin, token }) {
  const [schedules, setSchedules] = useState([]);
  const [loadingSchedules, setLoadingSchedules] = useState(false);
  const [scheduleError, setScheduleError] = useState("");
  const [scheduleMessage, setScheduleMessage] = useState("");
  const [scheduleForm, setScheduleForm] = useState({ cron_expr: "*/30 * * * *", agent_id: "" });
  const [agents, setAgents] = useState([]);
  const [tenantId, setTenantId] = useState("");
  const { tenants } = useUIStore();

  useEffect(() => {
    if (module) {
      loadSchedules(module.id);
    }
  }, [module]);

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

  const loadSchedules = async (moduleId) => {
    setLoadingSchedules(true);
    setScheduleError("");
    try {
      const qs = `?module_id=${moduleId}`;
      const res = await fetch(`${API_BASE}/schedules${qs}`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setSchedules(Array.isArray(data) ? data : []);
    } catch (err) {
      setScheduleError(err.message || "Unable to load schedules");
    } finally {
      setLoadingSchedules(false);
    }
  };

  const createSchedule = async () => {
    setScheduleError("");
    setScheduleMessage("");
    let agentId = scheduleForm.agent_id.trim();
    if (agentId) {
      const parsed = Number(agentId);
      if (isNaN(parsed) || parsed < 0) {
        setScheduleError("Agent ID must be numeric.");
        return;
      }
      agentId = parsed;
    } else {
      agentId = null;
    }

    try {
      const payload = {
        module_id: module.id,
        cron_expr: scheduleForm.cron_expr.trim() || "*/30 * * * *",
        agent_id: agentId,
      };
      if (isAdmin && tenantId) {
        payload.tenant_id = Number(tenantId);
      }
      const res = await fetch(`${API_BASE}/schedules`, {
        method: "POST",
        headers: authHeaders(token),
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      setScheduleMessage("Schedule created.");
      setScheduleForm((prev) => ({ ...prev, agent_id: "" }));
      loadSchedules(module.id);
    } catch (err) {
      setScheduleError(err.message || "Unable to create schedule");
    }
  };

  const deleteSchedule = async (scheduleId) => {
    setScheduleError("");
    try {
      const res = await fetch(`${API_BASE}/schedules/${scheduleId}`, {
        method: "DELETE",
        headers: authHeaders(token),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      setScheduleMessage("Schedule removed.");
      loadSchedules(module.id);
    } catch (err) {
      setScheduleError(err.message || "Unable to delete schedule");
    }
  };

  const scheduleColumns = [
    { key: "cron_expr", label: "Cron" },
    { key: "agent_id", label: "Agent" },
    { key: "next_run_at", label: "Next Run", render: (v) => formatDate(v) },
    { key: "status", label: "Status", render: (v) => v?.toUpperCase() ?? v },
    {
      key: "actions",
      label: "",
      render: (v, row) => (
        <Button variant="ghost" onClick={() => deleteSchedule(row.id)} className="text-red-600 hover:text-red-900">
          Remove
        </Button>
      ),
    },
  ];

  return (
    <div>
      <h3 className="mb-4 text-xl font-bold">Schedules</h3>
      {scheduleError && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{scheduleError}</div>}
      {scheduleMessage && <div className="mb-4 rounded-md bg-green-100 p-4 text-green-700">{scheduleMessage}</div>}

      {isAdmin && (
        <div className="mb-6 rounded-lg border bg-white p-4 shadow-sm">
          <h4 className="mb-4 text-lg font-medium">Create New Schedule</h4>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Cron Expression</label>
              <input
                value={scheduleForm.cron_expr}
                onChange={(e) => setScheduleForm((prev) => ({ ...prev, cron_expr: e.target.value }))}
                placeholder="*/30 * * * *"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Agent ID (optional)</label>
              <select
                value={scheduleForm.agent_id}
                onChange={(e) => setScheduleForm((prev) => ({ ...prev, agent_id: e.target.value }))}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              >
                <option value="">Unassigned</option>
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name} (#{agent.id})
                  </option>
                ))}
              </select>
            </div>
            {isAdmin && (
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
            )}
          </div>
          <Button onClick={createSchedule} className="mt-4">Create Schedule</Button>
        </div>
      )}

      <h4 className="mb-2 text-lg font-medium">Existing Schedules</h4>
      {loadingSchedules ? (
        <p>Loading schedules...</p>
      ) : schedules.length === 0 ? (
        <p>No schedules defined for this module.</p>
      ) : (
        <Table columns={scheduleColumns} rows={schedules} empty="No schedules defined for this module." />
      )}
    </div>
  );
}
