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
const fetchRetentionData = async (token, endpoint, options = {}) => {
  const res = await fetch(`${API_BASE}${endpoint}`, { headers: authHeaders(token), ...options });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};
function RetentionExports() {
  const [policy, setPolicy] = useState(null);
  const [exports, setExports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [retentionDays, setRetentionDays] = useState(90);
  const [archive, setArchive] = useState("vault");
  const [formats, setFormats] = useState("csv,json,pdf,zip");
  const [exportType, setExportType] = useState("alerts");
  const [exportFormats, setExportFormats] = useState("csv,json");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadData = useCallback(async () => {
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const [policyResp, exportResp] = await Promise.all([
        fetchRetentionData(token, "/retention/policy"),
        fetchRetentionData(token, "/retention/exports")
      ]);
      setPolicy(policyResp);
      setRetentionDays(policyResp?.retention_days ?? 90);
      setArchive(policyResp?.archive_storage ?? "vault");
      setFormats((policyResp?.export_formats || []).join(",") || "csv,json,pdf,zip");
      setExports(exportResp || []);
    } catch (err) {
      setError(err.message || "Failed to load retention data");
    } finally {
      setLoading(false);
    }
  }, [token]);
  useEffect(() => {
    loadData();
  }, [loadData]);
  const updatePolicy = async () => {
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const update = {
        retention_days: Number(retentionDays),
        archive_storage: archive,
        export_formats: formats.split(",").map((f) => f.trim()).filter(Boolean)
      };
      const resp = await fetchRetentionData(token, "/retention/policy", { method: "PUT", body: JSON.stringify(update) });
      setPolicy(resp);
      setMessage("Retention policy updated.");
    } catch (err) {
      setError(err.message || "Failed to update retention policy");
    } finally {
      setLoading(false);
    }
  };
  const requestExport = async () => {
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const formatsList = exportFormats.split(",").map((f) => f.trim()).filter(Boolean);
      const resp = await fetchRetentionData(token, "/retention/exports", { method: "POST", body: JSON.stringify({ export_type: exportType, formats: formatsList }) });
      setExports((prev) => [resp, ...prev]);
      setMessage("Export queued and completed. Download via storage URI.");
    } catch (err) {
      setError(err.message || "Failed to request export");
    } finally {
      setLoading(false);
    }
  };
  const exportColumns = [
    { key: "requested_at", label: "Requested" },
    { key: "export_type", label: "Type" },
    { key: "formats", label: "Formats", render: (v) => Array.isArray(v) ? v.join(", ") : v },
    { key: "status", label: "Status" },
    { key: "storage_uri", label: "Storage URI", render: (v) => v ? /* @__PURE__ */ jsx("code", { className: "text-xs", children: v }) : "-" }
  ];
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8 flex items-center justify-between", children: [
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Retention & Exports" }),
        /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Configure tenant retention policies and generate exports for auditors, regulators, or downstream analysis." })
      ] }),
      /* @__PURE__ */ jsx(Button, { onClick: loadData, disabled: loading, children: loading ? "Refreshing..." : "Reload" })
    ] }),
    message && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-green-100 p-4 text-green-700", children: message }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-8 md:grid-cols-2", children: [
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Retention Policy" }),
        /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Retention Days" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "number",
                min: 30,
                max: 1825,
                value: retentionDays,
                onChange: (e) => setRetentionDays(e.target.value),
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Archive Storage Tier" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                value: archive,
                onChange: (e) => setArchive(e.target.value),
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Allowed Export Formats (comma separated)" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                value: formats,
                onChange: (e) => setFormats(e.target.value),
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsx(Button, { onClick: updatePolicy, disabled: loading, children: "Update Policy" })
        ] })
      ] }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Request Export" }),
        /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Export Type" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                value: exportType,
                onChange: (e) => setExportType(e.target.value),
                placeholder: "Export type (e.g. alerts)",
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Formats (comma separated)" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                value: exportFormats,
                onChange: (e) => setExportFormats(e.target.value),
                placeholder: "Formats",
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsx(Button, { onClick: requestExport, disabled: loading, children: "Request Export" })
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsx("div", { className: "mt-8", children: /* @__PURE__ */ jsxs(Card, { children: [
      /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Exports" }),
      /* @__PURE__ */ jsx(Table, { columns: exportColumns, rows: exports, empty: "No exports generated yet." })
    ] }) })
  ] });
}
export {
  RetentionExports as default
};
