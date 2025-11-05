import { jsx, jsxs } from "react/jsx-runtime";
import { useReducer, useCallback, useEffect } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { T as Table } from "./Table-CLWnewy9.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
function Services({ services, baseline }) {
  const columns = [
    { key: "name", label: "Name" },
    { key: "status", label: "Status" },
    { key: "start_mode", label: "Start" },
    { key: "run_account", label: "Account" },
    { key: "binary_path", label: "Path" }
  ];
  const rows = services.map((service) => {
    const baselineService = baseline.find(
      (b) => b.name?.toLowerCase() === service.name?.toLowerCase()
    );
    const isMismatch = baselineService && (baselineService.expected_status && baselineService.expected_status !== service.status || baselineService.expected_start_mode && baselineService.expected_start_mode !== service.start_mode || baselineService.expected_run_account && baselineService.expected_run_account !== service.run_account || baselineService.expected_hash && baselineService.expected_hash !== service.hash);
    return {
      ...service,
      isMismatch
    };
  });
  return /* @__PURE__ */ jsx(
    Table,
    {
      columns,
      rows,
      empty: "No services found.",
      rowClassName: (row) => row.isMismatch ? "bg-red-50" : ""
    }
  );
}
function Registry({ registry, baseline }) {
  const columns = [
    { key: "hive", label: "Hive" },
    { key: "key_path", label: "Key" },
    { key: "value_name", label: "Name" },
    { key: "value_data", label: "Value" },
    { key: "value_type", label: "Type" }
  ];
  const rows = registry.map((entry) => {
    const baselineEntry = baseline.find(
      (b) => b.hive?.toUpperCase() === entry.hive?.toUpperCase() && b.key_path === entry.key_path && b.value_name === entry.value_name
    );
    const isMismatch = baselineEntry && (baselineEntry.expected_value && baselineEntry.expected_value !== entry.value_data || baselineEntry.expected_type && baselineEntry.expected_type !== entry.value_type);
    return {
      ...entry,
      isMismatch
    };
  });
  return /* @__PURE__ */ jsx(
    Table,
    {
      columns,
      rows,
      empty: "No registry entries found.",
      rowClassName: (row) => row.isMismatch ? "bg-red-50" : ""
    }
  );
}
function Tasks({ tasks }) {
  const columns = [
    { key: "name", label: "Name" },
    { key: "task_type", label: "Type" },
    { key: "schedule", label: "Schedule" },
    { key: "command", label: "Command" }
  ];
  return /* @__PURE__ */ jsx(Table, { columns, rows: tasks, empty: "No tasks found." });
}
function ServiceBaseline({ baseline, setBaseline, onSave }) {
  const addRow = () => {
    setBaseline([
      ...baseline,
      {
        name: "",
        expected_status: "",
        expected_start_mode: "",
        expected_hash: "",
        expected_run_account: "",
        is_critical: false,
        notes: ""
      }
    ]);
  };
  const removeRow = (index) => {
    setBaseline(baseline.filter((_, i) => i !== index));
  };
  const handleChange = (index, field, value) => {
    const newBaseline = [...baseline];
    newBaseline[index][field] = value;
    setBaseline(newBaseline);
  };
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium", children: "Service Baseline" }),
      /* @__PURE__ */ jsxs("div", { className: "flex space-x-4", children: [
        /* @__PURE__ */ jsx(Button, { onClick: addRow, children: "Add" }),
        /* @__PURE__ */ jsx(Button, { onClick: onSave, children: "Save" })
      ] })
    ] }),
    /* @__PURE__ */ jsx("div", { className: "mt-4 overflow-x-auto", children: /* @__PURE__ */ jsxs("table", { className: "min-w-full divide-y divide-gray-200", children: [
      /* @__PURE__ */ jsx("thead", { className: "bg-gray-50", children: /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Name" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Status" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Start" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Run Account" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Hash" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Critical" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Notes" }),
        /* @__PURE__ */ jsx("th", { className: "relative px-6 py-3", children: /* @__PURE__ */ jsx("span", { className: "sr-only", children: "Remove" }) })
      ] }) }),
      /* @__PURE__ */ jsx("tbody", { className: "divide-y divide-gray-200 bg-white", children: baseline.map((row, index) => /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.name || "",
            onChange: (e) => handleChange(index, "name", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.expected_status || "",
            onChange: (e) => handleChange(index, "expected_status", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.expected_start_mode || "",
            onChange: (e) => handleChange(index, "expected_start_mode", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.expected_run_account || "",
            onChange: (e) => handleChange(index, "expected_run_account", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.expected_hash || "",
            onChange: (e) => handleChange(index, "expected_hash", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            type: "checkbox",
            checked: !!row.is_critical,
            onChange: (e) => handleChange(index, "is_critical", e.target.checked),
            className: "h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.notes || "",
            onChange: (e) => handleChange(index, "notes", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4 text-right text-sm font-medium", children: /* @__PURE__ */ jsx(Button, { variant: "ghost", onClick: () => removeRow(index), children: "Remove" }) })
      ] }, index)) })
    ] }) })
  ] });
}
function RegistryBaseline({ baseline, setBaseline, onSave }) {
  const addRow = () => {
    setBaseline([
      ...baseline,
      {
        hive: "HKLM",
        key_path: "",
        value_name: "",
        expected_value: "",
        expected_type: "",
        is_critical: false,
        notes: ""
      }
    ]);
  };
  const removeRow = (index) => {
    setBaseline(baseline.filter((_, i) => i !== index));
  };
  const handleChange = (index, field, value) => {
    const newBaseline = [...baseline];
    newBaseline[index][field] = value;
    setBaseline(newBaseline);
  };
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium", children: "Registry Baseline" }),
      /* @__PURE__ */ jsxs("div", { className: "flex space-x-4", children: [
        /* @__PURE__ */ jsx(Button, { onClick: addRow, children: "Add" }),
        /* @__PURE__ */ jsx(Button, { onClick: onSave, children: "Save" })
      ] })
    ] }),
    /* @__PURE__ */ jsx("div", { className: "mt-4 overflow-x-auto", children: /* @__PURE__ */ jsxs("table", { className: "min-w-full divide-y divide-gray-200", children: [
      /* @__PURE__ */ jsx("thead", { className: "bg-gray-50", children: /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Hive" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Key" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Name" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Expected Value" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Type" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Critical" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Notes" }),
        /* @__PURE__ */ jsx("th", { className: "relative px-6 py-3", children: /* @__PURE__ */ jsx("span", { className: "sr-only", children: "Remove" }) })
      ] }) }),
      /* @__PURE__ */ jsx("tbody", { className: "divide-y divide-gray-200 bg-white", children: baseline.map((row, index) => /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.hive || "",
            onChange: (e) => handleChange(index, "hive", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.key_path || "",
            onChange: (e) => handleChange(index, "key_path", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.value_name || "",
            onChange: (e) => handleChange(index, "value_name", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.expected_value || "",
            onChange: (e) => handleChange(index, "expected_value", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.expected_type || "",
            onChange: (e) => handleChange(index, "expected_type", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            type: "checkbox",
            checked: !!row.is_critical,
            onChange: (e) => handleChange(index, "is_critical", e.target.checked),
            className: "h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.notes || "",
            onChange: (e) => handleChange(index, "notes", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4 text-right text-sm font-medium", children: /* @__PURE__ */ jsx(Button, { variant: "ghost", onClick: () => removeRow(index), children: "Remove" }) })
      ] }, index)) })
    ] }) })
  ] });
}
function TaskBaseline({ baseline, setBaseline, onSave }) {
  const addRow = () => {
    setBaseline([
      ...baseline,
      {
        name: "",
        task_type: "cron",
        expected_schedule: "",
        expected_command: "",
        is_critical: false,
        notes: ""
      }
    ]);
  };
  const removeRow = (index) => {
    setBaseline(baseline.filter((_, i) => i !== index));
  };
  const handleChange = (index, field, value) => {
    const newBaseline = [...baseline];
    newBaseline[index][field] = value;
    setBaseline(newBaseline);
  };
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium", children: "Task Baseline" }),
      /* @__PURE__ */ jsxs("div", { className: "flex space-x-4", children: [
        /* @__PURE__ */ jsx(Button, { onClick: addRow, children: "Add" }),
        /* @__PURE__ */ jsx(Button, { onClick: onSave, children: "Save" })
      ] })
    ] }),
    /* @__PURE__ */ jsx("div", { className: "mt-4 overflow-x-auto", children: /* @__PURE__ */ jsxs("table", { className: "min-w-full divide-y divide-gray-200", children: [
      /* @__PURE__ */ jsx("thead", { className: "bg-gray-50", children: /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Name" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Type" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Expected Schedule" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Expected Command" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Critical" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Notes" }),
        /* @__PURE__ */ jsx("th", { className: "relative px-6 py-3", children: /* @__PURE__ */ jsx("span", { className: "sr-only", children: "Remove" }) })
      ] }) }),
      /* @__PURE__ */ jsx("tbody", { className: "divide-y divide-gray-200 bg-white", children: baseline.map((row, index) => /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.name || "",
            onChange: (e) => handleChange(index, "name", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.task_type || "",
            onChange: (e) => handleChange(index, "task_type", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.expected_schedule || "",
            onChange: (e) => handleChange(index, "expected_schedule", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.expected_command || "",
            onChange: (e) => handleChange(index, "expected_command", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            type: "checkbox",
            checked: !!row.is_critical,
            onChange: (e) => handleChange(index, "is_critical", e.target.checked),
            className: "h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: row.notes || "",
            onChange: (e) => handleChange(index, "notes", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4 text-right text-sm font-medium", children: /* @__PURE__ */ jsx(Button, { variant: "ghost", onClick: () => removeRow(index), children: "Remove" }) })
      ] }, index)) })
    ] }) })
  ] });
}
function Events({ events }) {
  const columns = [
    { key: "detected_at", label: "Time" },
    { key: "severity", label: "Severity" },
    { key: "event_type", label: "Type" },
    { key: "title", label: "Title" }
  ];
  return /* @__PURE__ */ jsx(Table, { columns, rows: events, empty: "No events found." });
}
function Diff({ serviceDiff, registryDiff }) {
  return /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-6 md:grid-cols-2", children: [
    /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium", children: "Service Changes" }),
      /* @__PURE__ */ jsx("pre", { className: "mt-4 overflow-auto rounded-lg bg-gray-800 p-4 text-sm text-white", children: /* @__PURE__ */ jsx("code", { children: JSON.stringify(serviceDiff, null, 2) }) })
    ] }),
    /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium", children: "Registry Changes" }),
      /* @__PURE__ */ jsx("pre", { className: "mt-4 overflow-auto rounded-lg bg-gray-800 p-4 text-sm text-white", children: /* @__PURE__ */ jsx("code", { children: JSON.stringify(registryDiff, null, 2) }) })
    ] })
  ] });
}
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
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
  svcIgnore: ""
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
function Integrity() {
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
        fetchData(`${API_BASE}/admin/settings/tenant`)
      ]);
      const regIgnore = settings?.find((s) => s.key === "integrity.registry.ignore_prefixes")?.value || "";
      const svcIgnore = settings?.find((s) => s.key === "integrity.service.ignore_names")?.value || "";
      dispatch({ type: "SET_DATA", data: { services, registry, tasks, svcBaseline, regBaseline, taskBaseline, regIgnore: Array.isArray(regIgnore) ? regIgnore.join(",") : regIgnore, svcIgnore: Array.isArray(svcIgnore) ? svcIgnore.join(",") : svcIgnore } });
      dispatch({ type: "SET_MSG", msg: "Refreshed." });
    } catch (e) {
      dispatch({ type: "SET_ERROR", error: e.message || "Refresh failed" });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
      setTimeout(() => dispatch({ type: "SET_MSG", msg: "" }), 2e3);
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
      setTimeout(() => dispatch({ type: "SET_MSG", msg: "" }), 2e3);
    }
  };
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsx("header", { className: "mb-8", children: /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Integrity" }) }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsx("div", { className: "grid grid-cols-1 gap-6 md:grid-cols-4" }) }),
    state.error && /* @__PURE__ */ jsx("div", { className: "mb-8 rounded-md bg-red-100 p-4 text-red-700", children: state.error }),
    state.msg && /* @__PURE__ */ jsx("div", { className: "mb-8 rounded-md bg-green-100 p-4 text-green-700", children: state.msg }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-8", children: [
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(Services, { services: state.services, baseline: state.svcBaseline }) }),
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(Registry, { registry: state.registry, baseline: state.regBaseline }) }),
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(Tasks, { tasks: state.tasks }) }),
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(ServiceBaseline, { baseline: state.svcBaseline, setBaseline: (value) => handleFieldChange("svcBaseline", value), onSave: () => handleSave(`${API_BASE}/integrity/services/baseline`, { agent_id: state.scope === "agent" && state.agentId ? Number(state.agentId) : null, entries: state.svcBaseline }) }) }),
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(RegistryBaseline, { baseline: state.regBaseline, setBaseline: (value) => handleFieldChange("regBaseline", value), onSave: () => handleSave(`${API_BASE}/integrity/registry/baseline`, { agent_id: state.scope === "agent" && state.agentId ? Number(state.agentId) : null, entries: state.regBaseline }) }) }),
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(TaskBaseline, { baseline: state.taskBaseline, setBaseline: (value) => handleFieldChange("taskBaseline", value), onSave: () => handleSave(`${API_BASE}/integrity/tasks/baseline`, { agent_id: state.scope === "agent" && state.agentId ? Number(state.agentId) : null, entries: state.taskBaseline }) }) }),
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(Events, { events: state.events }) }),
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(Diff, { serviceDiff: state.svcDiff, registryDiff: state.regDiff }) })
    ] })
  ] });
}
export {
  Integrity as default
};
