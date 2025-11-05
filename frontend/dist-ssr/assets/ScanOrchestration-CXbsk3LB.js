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
const fetchScanData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};
function ScanOrchestration() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadJobs = useCallback(async (status) => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchScanData(token, "/scan-orchestration/jobs", { status });
      setJobs(data || []);
      if (data?.length) {
        const jobId = data[0].id;
        setSelectedJob(jobId);
        loadJobDetails(jobId);
      }
    } catch (err) {
      setError(err.message || "Failed to load scan jobs");
    } finally {
      setLoading(false);
    }
  }, [token]);
  const loadJobDetails = async (jobId) => {
    if (!jobId) return;
    try {
      const detail = await fetchScanData(token, `/scan-orchestration/jobs/${jobId}`);
      setJobDetails(detail);
    } catch (err) {
      setError(err.message || "Failed to load job details");
    }
  };
  useEffect(() => {
    loadJobs(statusFilter);
  }, [loadJobs, statusFilter]);
  const handleJobSelection = (jobId) => {
    setSelectedJob(jobId);
    loadJobDetails(jobId);
  };
  const resultsColumns = [
    { key: "agent_id", label: "Agent" },
    { key: "asset_id", label: "Asset" },
    { key: "status", label: "Status", render: (v) => v?.toUpperCase() ?? v },
    { key: "details", label: "Details" }
  ];
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Scan Orchestration" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Coordinate vulnerability and discovery scans across tenants. Monitor job status, priority, and agent assignment from a single view." })
    ] }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
      /* @__PURE__ */ jsxs(
        "select",
        {
          value: statusFilter,
          onChange: (e) => setStatusFilter(e.target.value),
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "", children: "All jobs" }),
            /* @__PURE__ */ jsx("option", { value: "pending", children: "Pending" }),
            /* @__PURE__ */ jsx("option", { value: "running", children: "Running" }),
            /* @__PURE__ */ jsx("option", { value: "completed", children: "Completed" })
          ]
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: () => loadJobs(statusFilter), disabled: loading, children: loading ? "Refreshing..." : "Reload" })
    ] }) }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-8 md:grid-cols-3", children: [
      /* @__PURE__ */ jsx("div", { className: "md:col-span-1", children: /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx("div", { className: "space-y-4", children: jobs.length ? jobs.map((job) => /* @__PURE__ */ jsxs(
        "button",
        {
          onClick: () => handleJobSelection(job.id),
          className: `w-full rounded-lg border p-4 text-left ${selectedJob === job.id ? "border-facebook-blue bg-blue-50" : "border-gray-200 bg-white"}`,
          children: [
            /* @__PURE__ */ jsx("div", { className: "font-semibold", children: job.name }),
            /* @__PURE__ */ jsxs("div", { className: "text-sm text-gray-500", children: [
              job.scan_type,
              " • Priority ",
              job.priority
            ] }),
            /* @__PURE__ */ jsxs("div", { className: "text-xs text-gray-500", children: [
              job.status.toUpperCase(),
              " • Created ",
              job.created_at
            ] })
          ]
        },
        job.id
      )) : /* @__PURE__ */ jsx("div", { className: "text-center text-gray-500", children: "No scan jobs." }) }) }) }),
      /* @__PURE__ */ jsx("div", { className: "md:col-span-2", children: /* @__PURE__ */ jsx(Card, { children: !jobDetails ? /* @__PURE__ */ jsx("div", { className: "text-center text-gray-500", children: "Select a job to view execution details." }) : /* @__PURE__ */ jsxs("div", { className: "space-y-6", children: [
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("h2", { className: "text-2xl font-bold", children: jobDetails.job.name }),
          /* @__PURE__ */ jsx("p", { className: "mt-1 text-sm text-gray-600", children: jobDetails.job.description || "No description provided." }),
          /* @__PURE__ */ jsxs("div", { className: "mt-4 text-sm text-gray-500", children: [
            "Type: ",
            jobDetails.job.scan_type,
            " • Priority ",
            jobDetails.job.priority,
            " • Status ",
            jobDetails.job.status.toUpperCase()
          ] }),
          /* @__PURE__ */ jsxs("div", { className: "text-xs text-gray-500", children: [
            "Created ",
            jobDetails.job.created_at,
            " • Started ",
            jobDetails.job.started_at || "-",
            " • Completed ",
            jobDetails.job.completed_at || "-"
          ] })
        ] }),
        /* @__PURE__ */ jsx(Table, { columns: resultsColumns, rows: jobDetails.results, empty: "No results yet." }),
        /* @__PURE__ */ jsx(Button, { onClick: () => loadJobDetails(selectedJob), disabled: loading, children: "Refresh Job" })
      ] }) }) })
    ] })
  ] });
}
export {
  ScanOrchestration as default
};
