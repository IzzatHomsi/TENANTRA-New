import React, { useCallback, useEffect, useMemo, useState } from "react";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { getApiBase } from "../utils/apiBase";

const API_BASE = getApiBase();

export default function AgentManagement() {
  const { token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [modules, setModules] = useState([]);
  const [mappings, setMappings] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState(null);
  const [newAgentName, setNewAgentName] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [enrollToken, setEnrollToken] = useState(null);
  const authHeaders = useMemo(
    () => (token ? { Authorization: `Bearer ${token}` } : {}),
    [token]
  );

  const fetchJson = useCallback(async (path) => {
    const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(text || `HTTP ${res.status}`);
    }
    return res.json();
  }, [authHeaders]);

  const loadData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [agentList, moduleList, mappingList] = await Promise.all([
        fetchJson("/admin/agents"),
        fetchJson("/modules/"),
        fetchJson("/modules/mapping"),
      ]);
      setAgents(agentList || []);
      setModules(moduleList || []);
      setMappings(mappingList || []);
      setSelectedAgentId((current) => {
        if (current != null || !(agentList?.length)) {
          return current;
        }
        return agentList[0].id;
      });
    } catch (err) {
      setError(err.message || "Failed to load agent data");
    } finally {
      setLoading(false);
    }
  }, [fetchJson, token]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const selectedAgent = useMemo(
    () => agents.find((agent) => agent.id === selectedAgentId),
    [agents, selectedAgentId]
  );

  const agentOverrideMap = useMemo(() => {
    if (!selectedAgentId) return new Map();
    return new Map(
      mappings
        .filter((entry) => entry.agent_id === selectedAgentId)
        .map((entry) => [entry.module_id, entry.enabled])
    );
  }, [mappings, selectedAgentId]);

  const handleCreateAgent = async (event) => {
    event.preventDefault();
    if (!newAgentName.trim()) {
      setError("Agent name is required");
      return;
    }
    setError("");
    setMessage("");
    try {
      const res = await fetch(`${API_BASE}/agents/enroll`, {
        method: "POST",
        headers: { ...authHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({ name: newAgentName.trim() }),
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data = await res.json();
      setEnrollToken(data);
      setNewAgentName("");
      await loadData();
      setMessage("Agent enrolled. Save the token for the agent installer.");
    } catch (err) {
      setError(err.message || "Unable to create agent");
    }
  };

  const handleMappingChange = async (moduleId, nextMode) => {
    if (!selectedAgentId) return;
    setMessage("");
    try {
      if (nextMode === "inherit") {
        await fetch(`${API_BASE}/modules/mapping/${selectedAgentId}/${moduleId}`, {
          method: "DELETE",
          headers: authHeaders,
        });
      } else {
        const enabled = nextMode === "force-on";
        await fetch(`${API_BASE}/modules/mapping`, {
          method: "PUT",
          headers: { ...authHeaders, "Content-Type": "application/json" },
          body: JSON.stringify([{ agent_id: selectedAgentId, module_id: moduleId, enabled }]),
        });
      }
      const mappingData = await fetchJson("/modules/mapping");
      setMappings(mappingData || []);
      setMessage("Module preferences updated.");
    } catch (err) {
      setError(err.message || "Failed to update module preferences");
    }
  };

  const moduleRows = useMemo(() => {
    return modules.map((module) => {
      const override = agentOverrideMap.get(module.id);
      const value = override === true ? "force-on" : override === false ? "force-off" : "inherit";
      const effective = override != null ? override : module.enabled;
      return {
        ...module,
        overrideValue: value,
        effective,
        tenantDefault: module.enabled,
      };
    });
  }, [agentOverrideMap, modules]);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-semibold text-primary-text">Agent Management</h1>
        <p className="text-sm text-secondary-text">
          Enroll agents and control which modules they are allowed to execute.
        </p>
      </header>

      <ErrorBanner message={error} onClose={() => setError("")} />
      {message && (
        <div className="rounded-md border border-secondary/30 bg-secondary/10 p-3 text-sm text-secondary">
          {message}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-primary-text">Agents</h2>
            <Button size="sm" variant="ghost" onClick={loadData} disabled={loading}>
              Refresh
            </Button>
          </div>
          <form onSubmit={handleCreateAgent} className="space-y-2">
            <label className="block text-sm font-medium text-primary-text">Agent display name</label>
            <input
              type="text"
              value={newAgentName}
              onChange={(event) => setNewAgentName(event.target.value)}
              className="w-full rounded-md border border-border-color px-3 py-2 text-sm"
              placeholder="e.g. prod-edge-01"
            />
            <Button type="submit" className="w-full" disabled={!newAgentName.trim()}>
              Enroll agent
            </Button>
          </form>
          {enrollToken && (
            <div className="rounded-md border border-border-color bg-neutral p-3 text-xs text-primary-text">
              <div className="font-semibold mb-1">Enrollment token</div>
              <div className="font-mono break-all">{enrollToken.token}</div>
              <p className="mt-2 text-secondary-text">
                Pair this token with agent <strong>#{enrollToken.agent_id}</strong>. It will not be shown again.
              </p>
            </div>
          )}
          <div className="max-h-[320px] overflow-y-auto border-t border-border-color pt-3">
            {agents.length === 0 ? (
              <p className="text-sm text-secondary-text">No agents enrolled yet.</p>
            ) : (
              <ul className="space-y-2">
                {agents.map((agent) => (
                  <li key={agent.id}>
                    <button
                      type="button"
                      onClick={() => setSelectedAgentId(agent.id)}
                      className={`w-full rounded-md border px-3 py-2 text-left text-sm ${
                        selectedAgentId === agent.id
                          ? "border-primary bg-blue-50 text-primary-text"
                          : "border-border-color bg-surface"
                      }`}
                    >
                      <div className="font-medium">{agent.name}</div>
                      <div className="text-xs text-secondary-text">
                        ID #{agent.id} • {agent.is_active ? "Active" : "Disabled"}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Card>

        <Card className="lg:col-span-2 space-y-4" padded={false}>
          <div className="border-b border-border-color px-4 py-3">
            <h2 className="text-lg font-semibold text-primary-text">
              {selectedAgent ? selectedAgent.name : "Select an agent"}
            </h2>
            <p className="text-sm text-secondary-text">
              Configure module overrides per agent. By default agents inherit tenant module settings.
            </p>
          </div>
          {selectedAgent ? (
            <div className="px-4 pb-4">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-secondary-text">
                      <th className="py-2 pr-4">Module</th>
                      <th className="py-2 pr-4">Tenant default</th>
                      <th className="py-2 pr-4">Effective</th>
                      <th className="py-2 pr-4">Override</th>
                    </tr>
                  </thead>
                  <tbody>
                    {moduleRows.map((module) => (
                      <tr key={module.id} className="border-t border-border-color/60">
                        <td className="py-2 pr-4">
                          <div className="font-medium text-primary-text">{module.name}</div>
                          <div className="text-xs text-secondary-text">{module.category || "Uncategorised"}</div>
                        </td>
                        <td className="py-2 pr-4">
                          {module.tenantDefault ? (
                            <span className="text-success font-medium">Enabled</span>
                          ) : (
                            <span className="text-danger font-medium">Disabled</span>
                          )}
                        </td>
                        <td className="py-2 pr-4">
                          {module.effective ? (
                            <span className="text-success font-medium">Enabled</span>
                          ) : (
                            <span className="text-danger font-medium">Disabled</span>
                          )}
                        </td>
                        <td className="py-2 pr-4">
                          <select
                            value={module.overrideValue}
                            onChange={(event) => handleMappingChange(module.id, event.target.value)}
                            className="rounded-md border border-border-color bg-surface px-2 py-1 text-sm"
                          >
                            <option value="inherit">
                              Inherit ({module.tenantDefault ? "Enabled" : "Disabled"})
                            </option>
                            <option value="force-on">Force On</option>
                            <option value="force-off">Force Off</option>
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="px-4 py-6 text-sm text-secondary-text">Select an agent to manage module overrides.</div>
          )}
        </Card>
      </div>
    </div>
  );
}
