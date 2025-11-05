import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useCallback, useEffect, useMemo } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const API_BASE = getApiBase();
const authHeaders = (token, extra = {}) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
  ...extra
});
function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({
    page: 1,
    pageSize: 50,
    userId: "",
    start: "",
    end: "",
    result: ""
  });
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const qs = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          qs.set(key, value);
        }
      });
      const res = await fetch(`${API_BASE}/audit-logs?${qs.toString()}`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setLogs(data?.items || []);
      setTotal(data?.total || 0);
    } catch (e) {
      setError(e.message || "Failed to load audit logs");
    } finally {
      setLoading(false);
    }
  }, [token, filters]);
  useEffect(() => {
    loadLogs();
  }, [loadLogs]);
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value, page: 1 }));
  };
  const exportCsv = async () => {
    try {
      const qs = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value && key !== "page" && key !== "pageSize") {
          qs.set(key, value);
        }
      });
      const res = await fetch(`${API_BASE}/audit-logs/export?${qs.toString()}`, {
        headers: authHeaders(token, { Accept: "text/csv" })
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "audit_logs.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert(e?.message || "Failed to export");
    }
  };
  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / filters.pageSize)), [total, filters.pageSize]);
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8 flex items-center justify-between", children: [
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Audit Logs" }),
        /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Filter, review, and export platform audit logs." })
      ] }),
      /* @__PURE__ */ jsx(Button, { onClick: exportCsv, children: "Export CSV" })
    ] }),
    /* @__PURE__ */ jsxs(Card, { children: [
      /* @__PURE__ */ jsxs("div", { className: "mb-4 grid grid-cols-1 gap-4 md:grid-cols-5", children: [
        /* @__PURE__ */ jsx(
          "input",
          {
            name: "userId",
            value: filters.userId,
            onChange: handleFilterChange,
            placeholder: "User ID",
            className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ),
        /* @__PURE__ */ jsx(
          "input",
          {
            type: "date",
            name: "start",
            value: filters.start,
            onChange: handleFilterChange,
            className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ),
        /* @__PURE__ */ jsx(
          "input",
          {
            type: "date",
            name: "end",
            value: filters.end,
            onChange: handleFilterChange,
            className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ),
        /* @__PURE__ */ jsxs(
          "select",
          {
            name: "result",
            value: filters.result,
            onChange: handleFilterChange,
            className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
            children: [
              /* @__PURE__ */ jsx("option", { value: "", children: "Any result" }),
              /* @__PURE__ */ jsx("option", { value: "success", children: "Success" }),
              /* @__PURE__ */ jsx("option", { value: "failed", children: "Failed" }),
              /* @__PURE__ */ jsx("option", { value: "denied", children: "Denied" })
            ]
          }
        ),
        /* @__PURE__ */ jsx(
          "select",
          {
            name: "pageSize",
            value: filters.pageSize,
            onChange: handleFilterChange,
            className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
            children: [25, 50, 100, 200, 500].map((n) => /* @__PURE__ */ jsxs("option", { value: n, children: [
              n,
              "/page"
            ] }, n))
          }
        )
      ] }),
      error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
      /* @__PURE__ */ jsx("div", { className: "overflow-x-auto", children: /* @__PURE__ */ jsxs("table", { className: "min-w-full divide-y divide-gray-200", children: [
        /* @__PURE__ */ jsx("thead", { className: "bg-gray-50", children: /* @__PURE__ */ jsxs("tr", { children: [
          /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Timestamp" }),
          /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "User" }),
          /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Action" }),
          /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Result" }),
          /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "IP" }),
          /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Details" })
        ] }) }),
        /* @__PURE__ */ jsx("tbody", { className: "divide-y divide-gray-200 bg-white", children: loading ? /* @__PURE__ */ jsx("tr", { children: /* @__PURE__ */ jsx("td", { colSpan: 6, className: "py-12 text-center text-gray-500", children: "Loading..." }) }) : logs.length === 0 ? /* @__PURE__ */ jsx("tr", { children: /* @__PURE__ */ jsx("td", { colSpan: 6, className: "py-12 text-center text-gray-500", children: "No audit logs found." }) }) : logs.map((log) => /* @__PURE__ */ jsxs("tr", { children: [
          /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: log.timestamp }),
          /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: log.user_id ?? "-" }),
          /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: log.action }),
          /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: log.result }),
          /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: log.ip || "-" }),
          /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4 text-xs text-gray-700", children: log.details || "-" })
        ] }, `${log.timestamp}-${log.user_id}-${log.action}`)) })
      ] }) }),
      /* @__PURE__ */ jsxs("div", { className: "mt-4 flex items-center justify-between", children: [
        /* @__PURE__ */ jsxs("div", { className: "text-sm text-gray-500", children: [
          total,
          " results"
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-2", children: [
          /* @__PURE__ */ jsx(
            Button,
            {
              onClick: () => setFilters((prev) => ({ ...prev, page: Math.max(1, prev.page - 1) })),
              disabled: filters.page <= 1,
              children: "Prev"
            }
          ),
          /* @__PURE__ */ jsxs("div", { className: "text-sm", children: [
            "Page ",
            filters.page,
            " / ",
            pageCount
          ] }),
          /* @__PURE__ */ jsx(
            Button,
            {
              onClick: () => setFilters((prev) => ({ ...prev, page: Math.min(pageCount, prev.page + 1) })),
              disabled: filters.page >= pageCount,
              children: "Next"
            }
          )
        ] })
      ] })
    ] })
  ] });
}
export {
  AuditLogs as default
};
