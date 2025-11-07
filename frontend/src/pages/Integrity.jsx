import React, { useEffect, useReducer, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import Services from "../components/integrity/Services.jsx";
import Registry from "../components/integrity/Registry.jsx";
import Tasks from "../components/integrity/Tasks.jsx";
import ServiceBaseline from "../components/integrity/ServiceBaseline.jsx";
import RegistryBaseline from "../components/integrity/RegistryBaseline.jsx";
import TaskBaseline from "../components/integrity/TaskBaseline.jsx";
import Events from "../components/integrity/Events.jsx";
import Diff from "../components/integrity/Diff.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const initialState = {
  loading: true,
  error: "",
  msg: "",
  scope: "tenant",
  agentId: "",
  hive: "HKLM",
  keyPath: "",
  leftTs: "",
  rightTs: "",
  eventType: "",
  eventSeverity: "",
  services: [],
  registry: [],
  tasks: [],
  svcBaseline: [],
  regBaseline: [],
  taskBaseline: [],
  svcDiff: { added: [], removed: [], changed: [] },
  regDiff: { added: [], removed: [], modified: [] },
  events: [],
  regIgnore: "",
  svcIgnore: "",
};

function reducer(state, action) {
  switch (action.type) {
    case "SET_FIELD":
      return { ...state, [action.field]: action.value };
    case "SET_DATA":
      return { ...state, ...action.data };
    case "SET_LOADING":
      return { ...state, loading: action.loading };
    case "SET_ERROR":
      return { ...state, error: action.error };
    case "SET_MSG":
      return { ...state, msg: action.msg };
    default:
      return state;
  }
}

export default function Integrity() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const fetchData = useCallback(async (url, options = {}) => {
    const res = await fetch(url, { headers: authHeaders(token), ...options });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    return res.json();
  }, [token]);

  const refresh = useCallback(async () => {
    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: "" });
    dispatch({ type: "SET_MSG", msg: "" });
    try {
      const [services, registry, tasks, svcBaseline, regBaseline, taskBaseline, settings] = await Promise.all([
        fetchData(`${API_BASE}/integrity/services?agent_id=${state.agentId}`),
        fetchData(`${API_BASE}/integrity/registry?agent_id=${state.agentId}&hive=${state.hive}&key_path=${state.keyPath}`),
        fetchData(`${API_BASE}/integrity/tasks?agent_id=${state.agentId}`),
        fetchData(`${API_BASE}/integrity/services/baseline?agent_id=${state.agentId}`),
        fetchData(`${API_BASE}/integrity/registry/baseline?agent_id=${state.agentId}`),
        fetchData(`${API_BASE}/integrity/tasks/baseline?agent_id=${state.agentId}`),
        fetchData(`${API_BASE}/admin/settings/tenant`),
      ]);

      const regIgnore = settings?.find(s => s.key === "integrity.registry.ignore_prefixes")?.value || "";
      const svcIgnore = settings?.find(s => s.key === "integrity.service.ignore_names")?.value || "";

      dispatch({ type: "SET_DATA", data: { services, registry, tasks, svcBaseline, regBaseline, taskBaseline, regIgnore: Array.isArray(regIgnore) ? regIgnore.join(",") : regIgnore, svcIgnore: Array.isArray(svcIgnore) ? svcIgnore.join(",") : svcIgnore } });
      dispatch({ type: "SET_MSG", msg: "Refreshed." });
    } catch (e) {
      dispatch({ type: "SET_ERROR", error: e.message || "Refresh failed" });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
      setTimeout(() => dispatch({ type: "SET_MSG", msg: "" }), 2000);
    }
  }, [fetchData, state.agentId, state.hive, state.keyPath]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleFieldChange = (field, value) => {
    dispatch({ type: "SET_FIELD", field, value });
  };

  const handleSave = async (endpoint, body) => {
    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: "" });
    try {
      await fetchData(endpoint, { method: "POST", body: JSON.stringify(body) });
      dispatch({ type: "SET_MSG", msg: "Saved." });
    } catch (e) {
      dispatch({ type: "SET_ERROR", error: e.message || "Save failed" });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
      setTimeout(() => dispatch({ type: "SET_MSG", msg: "" }), 2000);
    }
  };

  const handleDiff = async () => {
    try {
      if (!state.agentId || !state.leftTs || !state.rightTs) return;
      const [svcDiff, regDiff] = await Promise.all([
        fetchData(`${API_BASE}/integrity/services/diff?agent_id=${state.agentId}&left=${state.leftTs}&right=${state.rightTs}`),
        fetchData(`${API_BASE}/integrity/registry/diff?agent_id=${state.agentId}&left=${state.leftTs}&right=${state.rightTs}&hive=${state.hive}`),
      ]);
      dispatch({ type: "SET_DATA", data: { svcDiff, regDiff } });
    } catch (e) {
      dispatch({ type: "SET_ERROR", error: e.message || "Diff failed" });
    }
  };

  const handleLoadEvents = async () => {
    try {
      const qs = new URLSearchParams({ agent_id: state.agentId, event_type: state.eventType, severity: state.eventSeverity });
      const events = await fetchData(`${API_BASE}/integrity/events?${qs.toString()}`);
      dispatch({ type: "SET_DATA", data: { events } });
    } catch (e) {
      dispatch({ type: "SET_ERROR", error: e.message || "Load events failed" });
    }
  };

  const handleSaveIgnores = async (target, scopeLevel = "tenant") => {
    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: "" });
    try {
      if (scopeLevel === "agent" && !state.agentId) {
        throw new Error("Agent ID required when saving agent ignores");
      }
      const baseKey = target === "registry" ? "integrity.registry.ignore_prefixes" : "integrity.service.ignore_names";
      const key = scopeLevel === "agent" ? `${baseKey}.agent.${state.agentId}` : baseKey;
      const rawValue = target === "registry" ? state.regIgnore : state.svcIgnore;
      const normalized = rawValue
        .split(/[\n,]/)
        .map((entry) => entry.trim())
        .filter(Boolean);
      await fetchData(`${API_BASE}/admin/settings/tenant`, {
        method: "PUT",
        body: JSON.stringify({ [key]: normalized }),
      });
      dispatch({ type: "SET_MSG", msg: "Saved." });
    } catch (e) {
      dispatch({ type: "SET_ERROR", error: e.message || "Save failed" });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
      setTimeout(() => dispatch({ type: "SET_MSG", msg: "" }), 2000);
    }
  };

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Integrity</h1>
      </header>

      <Card className="mb-8">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
          <label className="flex flex-col text-sm font-medium text-gray-700" htmlFor="integrityScope">
            Scope
            <select
              id="integrityScope"
              value={state.scope}
              onChange={(e) => handleFieldChange("scope", e.target.value)}
              className="mt-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            >
              <option value="tenant">Tenant</option>
              <option value="agent">Agent</option>
            </select>
          </label>
          <label className="flex flex-col text-sm font-medium text-gray-700" htmlFor="integrityAgentId">
            Agent ID
            <input
              id="integrityAgentId"
              type="number"
              value={state.agentId}
              onChange={(e) => handleFieldChange("agentId", e.target.value)}
              placeholder="Agent ID"
              className="mt-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              disabled={state.scope !== "agent"}
            />
          </label>
          <label className="flex flex-col text-sm font-medium text-gray-700" htmlFor="eventType">
            Type
            <input
              id="eventType"
              value={state.eventType}
              onChange={(e) => handleFieldChange("eventType", e.target.value)}
              placeholder="service_change"
              className="mt-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </label>
          <label className="flex flex-col text-sm font-medium text-gray-700" htmlFor="eventSeverity">
            Severity
            <select
              id="eventSeverity"
              value={state.eventSeverity}
              onChange={(e) => handleFieldChange("eventSeverity", e.target.value)}
              className="mt-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            >
              <option value="">Any</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </label>
        </div>
        <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-4">
          <label className="flex flex-col text-sm font-medium text-gray-700" htmlFor="diffLeft">
            Left
            <input
              id="diffLeft"
              type="datetime-local"
              value={state.leftTs}
              onChange={(e) => handleFieldChange("leftTs", e.target.value)}
              className="mt-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </label>
          <label className="flex flex-col text-sm font-medium text-gray-700" htmlFor="diffRight">
            Right
            <input
              id="diffRight"
              type="datetime-local"
              value={state.rightTs}
              onChange={(e) => handleFieldChange("rightTs", e.target.value)}
              className="mt-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </label>
        </div>
        <div className="mt-6 flex flex-wrap gap-4">
          <Button onClick={refresh} disabled={state.loading}>
            {state.loading ? "Refreshing..." : "Refresh"}
          </Button>
          <Button onClick={handleLoadEvents} disabled={state.loading}>
            Load
          </Button>
          <Button onClick={handleDiff} disabled={!state.agentId || !state.leftTs || !state.rightTs || state.loading}>
            Diff
          </Button>
        </div>
        <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <label className="flex flex-col text-sm font-medium text-gray-700" htmlFor="registryIgnores">
              Registry Ignores
              <textarea
                id="registryIgnores"
                placeholder="SOFTWARE\\..."
                value={state.regIgnore}
                onChange={(e) => handleFieldChange("regIgnore", e.target.value)}
                className="mt-1 min-h-[96px] rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </label>
            <div className="mt-2">
              <Button onClick={() => handleSaveIgnores("registry", "tenant")} disabled={state.loading}>
                Save Ignores
              </Button>
            </div>
          </div>
          <div>
            <label className="flex flex-col text-sm font-medium text-gray-700" htmlFor="svcIgAgent">
              Service Ignores
              <input
                id="svcIgAgent"
                placeholder="svc-example,svc-important"
                value={state.svcIgnore}
                onChange={(e) => handleFieldChange("svcIgnore", e.target.value)}
                className="mt-1 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </label>
            <div className="mt-2">
              <Button
                onClick={() => handleSaveIgnores("service", "agent")}
                disabled={state.scope !== "agent" || !state.agentId || state.loading}
              >
                Save Agent Ignores
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {state.error && <div className="mb-8 rounded-md bg-red-100 p-4 text-red-700">{state.error}</div>}
      {state.msg && <div className="mb-8 rounded-md bg-green-100 p-4 text-green-700">{state.msg}</div>}

      <div className="space-y-8">
        <Card>
          <Services services={state.services} baseline={state.svcBaseline} />
        </Card>
        <Card>
          <Registry registry={state.registry} baseline={state.regBaseline} />
        </Card>
        <Card>
          <Tasks tasks={state.tasks} />
        </Card>
        <Card>
          <ServiceBaseline baseline={state.svcBaseline} setBaseline={(value) => handleFieldChange("svcBaseline", value)} onSave={() => handleSave(`${API_BASE}/integrity/services/baseline`, { agent_id: state.scope === "agent" && state.agentId ? Number(state.agentId) : null, entries: state.svcBaseline })} />
        </Card>
        <Card>
          <RegistryBaseline baseline={state.regBaseline} setBaseline={(value) => handleFieldChange("regBaseline", value)} onSave={() => handleSave(`${API_BASE}/integrity/registry/baseline`, { agent_id: state.scope === "agent" && state.agentId ? Number(state.agentId) : null, entries: state.regBaseline })} />
        </Card>
        <Card>
          <TaskBaseline baseline={state.taskBaseline} setBaseline={(value) => handleFieldChange("taskBaseline", value)} onSave={() => handleSave(`${API_BASE}/integrity/tasks/baseline`, { agent_id: state.scope === "agent" && state.agentId ? Number(state.agentId) : null, entries: state.taskBaseline })} />
        </Card>
        <Card>
          <Events events={state.events} />
        </Card>
        <Card>
          <Diff serviceDiff={state.svcDiff} registryDiff={state.regDiff} />
        </Card>
      </div>
    </div>
  );
}
