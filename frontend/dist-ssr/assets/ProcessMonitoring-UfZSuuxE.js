import { jsxs, jsx } from "react/jsx-runtime";
import React, { useReducer, useCallback, useEffect } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import { T as Table } from "./Table-CLWnewy9.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const processColumns = [
  { key: "pid", label: "PID" },
  { key: "process_name", label: "Process" },
  { key: "username", label: "User" },
  { key: "executable_path", label: "Path" },
  { key: "hash", label: "SHA256" },
  {
    key: "command_line",
    label: "Command",
    render: (value) => value ? /* @__PURE__ */ jsx("code", { className: "text-xs font-mono", children: value }) : "-"
  },
  { key: "collected_at", label: "Collected" }
];
function ProcessList({ processes, onUseAsBaseline }) {
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium", children: "Active Processes" }),
      /* @__PURE__ */ jsx("button", { onClick: onUseAsBaseline, disabled: !processes.length, className: "rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm", children: "Use snapshot as baseline" })
    ] }),
    /* @__PURE__ */ jsx("div", { className: "mt-4", children: /* @__PURE__ */ jsx(Table, { columns: processColumns, rows: processes, empty: "No process snapshot available." }) })
  ] });
}
const driftColumns = [
  { key: "detected_at", label: "Detected" },
  { key: "change_type", label: "Change" },
  { key: "process_name", label: "Process" },
  { key: "severity", label: "Severity" },
  {
    key: "details",
    label: "Details",
    render: (value) => value ? value : "-"
  }
];
function DriftEvents({ drift }) {
  const driftSummary = React.useMemo(() => {
    if (!drift.length) return "No drift events detected.";
    const counts = drift.reduce((acc, evt) => {
      acc[evt.change_type] = (acc[evt.change_type] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(counts).map(([change, count]) => `${change}: ${count}`).join(" | ");
  }, [drift]);
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium", children: "Drift Events" }),
    /* @__PURE__ */ jsx("p", { className: "mt-1 text-sm text-gray-600", children: driftSummary }),
    /* @__PURE__ */ jsx("div", { className: "mt-4", children: /* @__PURE__ */ jsx(Table, { columns: driftColumns, rows: drift, empty: "No drift events recorded." }) })
  ] });
}
function Baseline({ baseline, setBaseline, onSave, scopeLabel }) {
  const addBaselineEntry = () => {
    setBaseline([
      ...baseline,
      {
        process_name: "",
        executable_path: "",
        expected_hash: "",
        expected_user: "",
        is_critical: false,
        notes: ""
      }
    ]);
  };
  const removeBaselineEntry = (index) => {
    setBaseline(baseline.filter((_, idx) => idx !== index));
  };
  const updateBaselineEntry = (index, field, value) => {
    setBaseline(
      baseline.map((entry, idx) => idx === index ? { ...entry, [field]: value } : entry)
    );
  };
  const toggleCritical = (index) => {
    setBaseline(
      baseline.map(
        (entry, idx) => idx === index ? { ...entry, is_critical: !entry.is_critical } : entry
      )
    );
  };
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxs("h3", { className: "text-lg font-medium", children: [
        scopeLabel,
        " Baseline"
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex space-x-4", children: [
        /* @__PURE__ */ jsx(Button, { onClick: addBaselineEntry, children: "Add entry" }),
        /* @__PURE__ */ jsx(Button, { onClick: onSave, children: "Save baseline" })
      ] })
    ] }),
    /* @__PURE__ */ jsx("p", { className: "mt-1 text-sm text-gray-600", children: "Define expected processes, hashes, and critical entries. Baselines are evaluated when agents post new reports." }),
    /* @__PURE__ */ jsx("div", { className: "mt-4 overflow-x-auto", children: /* @__PURE__ */ jsxs("table", { className: "min-w-full divide-y divide-gray-200", children: [
      /* @__PURE__ */ jsx("thead", { className: "bg-gray-50", children: /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Process" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Path" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Expected hash" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Expected user" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Critical" }),
        /* @__PURE__ */ jsx("th", { className: "relative px-6 py-3", children: /* @__PURE__ */ jsx("span", { className: "sr-only", children: "Remove" }) })
      ] }) }),
      /* @__PURE__ */ jsx("tbody", { className: "divide-y divide-gray-200 bg-white", children: baseline.map((entry, index) => /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: entry.process_name,
            placeholder: "process.exe",
            onChange: (e) => updateBaselineEntry(index, "process_name", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: entry.executable_path,
            placeholder: "/usr/bin/process",
            onChange: (e) => updateBaselineEntry(index, "executable_path", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: entry.expected_hash,
            placeholder: "sha256...",
            onChange: (e) => updateBaselineEntry(index, "expected_hash", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            value: entry.expected_user,
            placeholder: "SYSTEM",
            onChange: (e) => updateBaselineEntry(index, "expected_user", e.target.value),
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            type: "checkbox",
            checked: entry.is_critical,
            onChange: () => toggleCritical(index),
            className: "h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
          }
        ) }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4 text-right text-sm font-medium", children: /* @__PURE__ */ jsx(Button, { variant: "ghost", onClick: () => removeBaselineEntry(index), children: "Remove" }) })
      ] }, index)) })
    ] }) })
  ] });
}
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
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
  message: ""
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
  notes: entry.notes || ""
});
function ProcessMonitoring() {
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
          fetch(`${API_BASE}/processes${query}`, { headers: authHeaders(token) }).then((res) => res.json()),
          fetch(`${API_BASE}/processes/drift${query}`, { headers: authHeaders(token) }).then((res) => res.json()),
          fetch(`${API_BASE}/processes/baseline${query}`, { headers: authHeaders(token) }).then((res) => res.json())
        ]);
        dispatch({ type: "SET_DATA", data: { processes: procResp ?? [], drift: driftResp?.events ?? [], baseline: (baselineResp?.entries ?? []).map(normalizeBaselineEntry) } });
      } else {
        const defaultBaseline = await fetch(`${API_BASE}/processes/baseline`, { headers: authHeaders(token) }).then((res) => res.json());
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
      notes: proc.collected_at ? `Seeded ${proc.collected_at}` : ""
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
      const entries = baseline.filter((entry) => entry.process_name.trim()).map((entry) => ({
        process_name: entry.process_name.trim(),
        executable_path: entry.executable_path?.trim() || null,
        expected_hash: entry.expected_hash?.trim() || null,
        expected_user: entry.expected_user?.trim() || null,
        is_critical: Boolean(entry.is_critical),
        notes: entry.notes?.trim() || null
      }));
      await fetch(`${API_BASE}/processes/baseline`, {
        method: "POST",
        headers: authHeaders(token),
        body: JSON.stringify({ agent_id: agentScope ? Number(agentScope) : null, processes: entries })
      });
      dispatch({ type: "SET_MESSAGE", message: "Baseline updated successfully." });
      await loadData();
    } catch (err) {
      dispatch({ type: "SET_ERROR", error: err.message || "Failed to save baseline" });
    } finally {
      dispatch({ type: "SET_SAVING_BASELINE", savingBaseline: false });
    }
  };
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Process Monitoring & Drift" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Monitor live processes reported by your agents, detect drift against saved baselines, and curate baseline definitions per agent or tenant." })
    ] }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
      /* @__PURE__ */ jsxs(
        "select",
        {
          value: scope,
          onChange: (e) => dispatch({ type: "SET_FIELD", field: "scope", value: e.target.value }),
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "agent", children: "Agent baseline" }),
            /* @__PURE__ */ jsx("option", { value: "tenant", children: "Tenant default baseline" })
          ]
        }
      ),
      scope === "agent" && /* @__PURE__ */ jsx(
        "input",
        {
          type: "number",
          value: agentId,
          onChange: (e) => dispatch({ type: "SET_FIELD", field: "agentId", value: e.target.value }),
          placeholder: "Agent ID (e.g. 42)",
          className: "w-40 rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: loadData, disabled: loading || scope === "agent" && !agentId.trim(), children: loading ? "Loading..." : `Refresh ${scope === "agent" ? "Agent" : "Tenant"}` })
    ] }) }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    message && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-green-100 p-4 text-green-700", children: message }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-8", children: [
      scope === "agent" && /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(ProcessList, { processes, onUseAsBaseline: handleUseCurrentProcessesAsBaseline }) }),
      scope === "agent" && /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(DriftEvents, { drift }) }),
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(Baseline, { baseline, setBaseline: (value) => dispatch({ type: "SET_FIELD", field: "baseline", value }), onSave: handleSaveBaseline, scopeLabel: scope === "agent" ? "Agent" : "Tenant" }) })
    ] })
  ] });
}
export {
  ProcessMonitoring as default
};
