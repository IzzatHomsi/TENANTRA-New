import React, { useCallback, useEffect, useReducer } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import ProcessList from "../components/processes/ProcessList.jsx";
import DriftEvents from "../components/processes/DriftEvents.jsx";
import Baseline from "../components/processes/Baseline.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const initialState = {
  scope: "agent",
  agentId: "",
  processes: [],
  drift: [],
  baseline: [],
  loading: false,
  savingBaseline: false,
  error: "",
  message: "",
};

function reducer(state, action) {
  switch (action.type) {
    case "SET_FIELD":
      return { ...state, [action.field]: action.value };
    case "SET_DATA":
      return { ...state, ...action.data };
    case "SET_LOADING":
      return { ...state, loading: action.loading };
    case "SET_SAVING_BASELINE":
      return { ...state, savingBaseline: action.savingBaseline };
    case "SET_ERROR":
      return { ...state, error: action.error };
    case "SET_MESSAGE":
      return { ...state, message: action.message };
    default:
      return state;
  }
}

const normalizeBaselineEntry = (entry) => ({
  process_name: entry.process_name || "",
  executable_path: entry.executable_path || "",
  expected_hash: entry.expected_hash || "",
  expected_user: entry.expected_user || "",
  is_critical: Boolean(entry.is_critical),
  notes: entry.notes || "",
});

export default function ProcessMonitoring() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { scope, agentId, processes, drift, baseline, loading, savingBaseline, error, message } = state;

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadData = useCallback(async () => {
    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: "" });
    dispatch({ type: "SET_MESSAGE", message: "" });
    try {
      if (scope === "agent") {
        if (!agentId.trim()) {
          throw new Error("Enter an agent ID to load process data.");
        }
        const query = `?agent_id=${encodeURIComponent(agentId.trim())}`;
        const [procResp, driftResp, baselineResp] = await Promise.all([
          fetch(`${API_BASE}/processes${query}`, { headers: authHeaders(token) }).then(res => res.json()),
          fetch(`${API_BASE}/processes/drift${query}`, { headers: authHeaders(token) }).then(res => res.json()),
          fetch(`${API_BASE}/processes/baseline${query}`, { headers: authHeaders(token) }).then(res => res.json()),
        ]);
        dispatch({ type: "SET_DATA", data: { processes: procResp ?? [], drift: driftResp?.events ?? [], baseline: (baselineResp?.entries ?? []).map(normalizeBaselineEntry) } });
      } else {
        const defaultBaseline = await fetch(`${API_BASE}/processes/baseline`, { headers: authHeaders(token) }).then(res => res.json());
        dispatch({ type: "SET_DATA", data: { baseline: (defaultBaseline?.entries ?? []).map(normalizeBaselineEntry), processes: [], drift: [] } });
      }
    } catch (err) {
      dispatch({ type: "SET_ERROR", error: err.message || "Failed to load process monitoring data" });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
    }
  }, [agentId, scope, token]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleUseCurrentProcessesAsBaseline = () => {
    if (!processes.length) {
      dispatch({ type: "SET_ERROR", error: "Load agent processes before seeding a baseline." });
      return;
    }
    const seeded = processes.map((proc) => ({
      process_name: proc.process_name || "",
      executable_path: proc.executable_path || "",
      expected_hash: proc.hash || "",
      expected_user: proc.username || "",
      is_critical: false,
      notes: proc.collected_at ? `Seeded ${proc.collected_at}` : "",
    }));
    dispatch({ type: "SET_FIELD", field: "baseline", value: seeded });
    dispatch({ type: "SET_MESSAGE", message: "Baseline pre-filled from current process snapshot. Review and save to apply." });
  };

  const handleSaveBaseline = async () => {
    dispatch({ type: "SET_SAVING_BASELINE", savingBaseline: true });
    dispatch({ type: "SET_ERROR", error: "" });
    dispatch({ type: "SET_MESSAGE", message: "" });
    try {
      const agentScope = scope === "agent" ? agentId.trim() : null;
      if (scope === "agent" && !agentScope) {
        throw new Error("Agent ID required when saving agent baseline");
      }
      const entries = baseline
        .filter((entry) => entry.process_name.trim())
        .map((entry) => ({
          process_name: entry.process_name.trim(),
          executable_path: entry.executable_path?.trim() || null,
          expected_hash: entry.expected_hash?.trim() || null,
          expected_user: entry.expected_user?.trim() || null,
          is_critical: Boolean(entry.is_critical),
          notes: entry.notes?.trim() || null,
        }));

      await fetch(`${API_BASE}/processes/baseline`, {
        method: "POST",
        headers: authHeaders(token),
        body: JSON.stringify({ agent_id: agentScope ? Number(agentScope) : null, processes: entries }),
      });
      dispatch({ type: "SET_MESSAGE", message: "Baseline updated successfully." });
      await loadData();
    } catch (err) {
      dispatch({ type: "SET_ERROR", error: err.message || "Failed to save baseline" });
    } finally {
      dispatch({ type: "SET_SAVING_BASELINE", savingBaseline: false });
    }
  };

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Process Monitoring & Drift</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitor live processes reported by your agents, detect drift against saved baselines, and curate baseline definitions per agent or tenant.
        </p>
      </header>

      <Card className="mb-8">
        <div className="flex items-center space-x-4">
          <select
            value={scope}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "scope", value: e.target.value })}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          >
            <option value="agent">Agent baseline</option>
            <option value="tenant">Tenant default baseline</option>
          </select>
          {scope === "agent" && (
            <input
              type="number"
              value={agentId}
              onChange={(e) => dispatch({ type: "SET_FIELD", field: "agentId", value: e.target.value })}
              placeholder="Agent ID (e.g. 42)"
              className="w-40 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          )}
          <Button onClick={loadData} disabled={loading || (scope === "agent" && !agentId.trim())}>
            {loading ? "Loading..." : `Refresh ${scope === "agent" ? "Agent" : "Tenant"}`}
          </Button>
        </div>
      </Card>

      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}
      {message && <div className="mb-4 rounded-md bg-green-100 p-4 text-green-700">{message}</div>}

      <div className="space-y-8">
        {scope === "agent" && (
          <Card>
            <ProcessList processes={processes} onUseAsBaseline={handleUseCurrentProcessesAsBaseline} />
          </Card>
        )}
        {scope === "agent" && (
          <Card>
            <DriftEvents drift={drift} />
          </Card>
        )}
        <Card>
          <Baseline baseline={baseline} setBaseline={(value) => dispatch({ type: "SET_FIELD", field: "baseline", value })} onSave={handleSaveBaseline} scopeLabel={scope === "agent" ? "Agent" : "Tenant"} />
        </Card>
      </div>
    </div>
  );
}