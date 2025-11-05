import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useCallback, useEffect } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import { T as Table } from "./Table-CLWnewy9.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
const fetchThreatData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};
function ThreatIntel() {
  const [feeds, setFeeds] = useState([]);
  const [hits, setHits] = useState([]);
  const [severity, setSeverity] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [feedData, hitData] = await Promise.all([
        fetchThreatData(token, "/threat-intel/feeds"),
        fetchThreatData(token, "/threat-intel/hits", { severity })
      ]);
      setFeeds(feedData || []);
      setHits(hitData || []);
    } catch (err) {
      setError(err.message || "Failed to load threat intelligence data");
    } finally {
      setLoading(false);
    }
  }, [token, severity]);
  useEffect(() => {
    loadData();
  }, [loadData]);
  const feedColumns = [
    { key: "name", label: "Name" },
    { key: "source", label: "Source" },
    { key: "feed_type", label: "Type" },
    { key: "enabled", label: "Status", render: (v) => v ? "Enabled" : "Disabled" },
    { key: "last_synced_at", label: "Last Sync" }
  ];
  const hitColumns = [
    { key: "detected_at", label: "Detected" },
    { key: "indicator_value", label: "Indicator" },
    { key: "indicator_type", label: "Type" },
    { key: "entity_type", label: "Entity", render: (v, row) => `${v}${row.entity_identifier ? ` (${row.entity_identifier})` : ""}` },
    { key: "severity", label: "Severity", render: (v) => v?.toUpperCase() ?? v },
    { key: "context", label: "Context" }
  ];
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Threat Intelligence" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Monitor IoC feeds and correlate inbound indicators with tenant assets. Severity filters help prioritise urgent activity." })
    ] }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
      /* @__PURE__ */ jsxs(
        "select",
        {
          value: severity,
          onChange: (e) => setSeverity(e.target.value),
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "", children: "All severities" }),
            /* @__PURE__ */ jsx("option", { value: "critical", children: "Critical" }),
            /* @__PURE__ */ jsx("option", { value: "high", children: "High" }),
            /* @__PURE__ */ jsx("option", { value: "medium", children: "Medium" }),
            /* @__PURE__ */ jsx("option", { value: "low", children: "Low" })
          ]
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: loadData, disabled: loading, children: loading ? "Refreshing..." : "Refresh" })
    ] }) }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-8", children: [
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Feeds" }),
        /* @__PURE__ */ jsx(Table, { columns: feedColumns, rows: feeds, empty: "No feeds configured." })
      ] }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Detections" }),
        /* @__PURE__ */ jsx(Table, { columns: hitColumns, rows: hits, empty: "No threat intelligence hits found." })
      ] })
    ] })
  ] });
}
export {
  ThreatIntel as default
};
