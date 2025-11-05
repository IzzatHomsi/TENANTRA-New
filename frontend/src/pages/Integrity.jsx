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

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Integrity</h1>
      </header>

      <Card className="mb-8">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
          {/* Filters */}
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
