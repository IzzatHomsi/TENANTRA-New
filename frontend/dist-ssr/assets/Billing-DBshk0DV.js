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
const fetchBillingData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};
function Billing() {
  const [plans, setPlans] = useState([]);
  const [usage, setUsage] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [filters, setFilters] = useState({ metric: "", status: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [planData, usageData, invoiceData] = await Promise.all([
        fetchBillingData(token, "/billing/plans"),
        fetchBillingData(token, "/billing/usage", { metric: filters.metric }),
        fetchBillingData(token, "/billing/invoices", { status: filters.status })
      ]);
      setPlans(planData || []);
      setUsage(usageData || []);
      setInvoices(invoiceData || []);
    } catch (err) {
      setError(err.message || "Failed to load billing data");
    } finally {
      setLoading(false);
    }
  }, [token, filters]);
  useEffect(() => {
    loadData();
  }, [loadData]);
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Usage & Billing" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Monitor tenant consumption metrics, subscription plans, and invoice history for MSP billing automation." })
    ] }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
      /* @__PURE__ */ jsx(
        "input",
        {
          name: "metric",
          value: filters.metric,
          onChange: handleFilterChange,
          placeholder: "Metric filter",
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      ),
      /* @__PURE__ */ jsxs(
        "select",
        {
          name: "status",
          value: filters.status,
          onChange: handleFilterChange,
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "", children: "All invoices" }),
            /* @__PURE__ */ jsx("option", { value: "pending", children: "Pending" }),
            /* @__PURE__ */ jsx("option", { value: "paid", children: "Paid" }),
            /* @__PURE__ */ jsx("option", { value: "overdue", children: "Overdue" })
          ]
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: loadData, disabled: loading, children: loading ? "Loading..." : "Refresh" })
    ] }) }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-8 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-8", children: [
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Billing Plans" }),
        /* @__PURE__ */ jsx(
          Table,
          {
            columns: [
              { key: "code", label: "Code" },
              { key: "name", label: "Plan" },
              {
                key: "base_rate",
                label: "Base Rate",
                render: (v, row) => `${row.currency || "USD"} ${v?.toFixed?.(2) ?? v}`
              },
              {
                key: "overage_rate",
                label: "Overage",
                render: (v, row) => `${row.currency || "USD"} ${v?.toFixed?.(2) ?? v}`
              },
              { key: "description", label: "Description" }
            ],
            rows: plans,
            empty: "No billing plans configured."
          }
        )
      ] }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Usage Metrics" }),
        /* @__PURE__ */ jsx(
          Table,
          {
            columns: [
              { key: "recorded_at", label: "Recorded" },
              { key: "metric", label: "Metric" },
              { key: "quantity", label: "Quantity" },
              { key: "window_start", label: "Window Start" },
              { key: "window_end", label: "Window End" }
            ],
            rows: usage,
            empty: "No usage recorded for the selected filters."
          }
        )
      ] }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Invoices" }),
        /* @__PURE__ */ jsx(
          Table,
          {
            columns: [
              { key: "period_start", label: "Period Start" },
              { key: "period_end", label: "Period End" },
              {
                key: "amount",
                label: "Amount",
                render: (v, row) => `${row.currency || "USD"} ${v?.toFixed?.(2) ?? v}`
              },
              { key: "status", label: "Status", render: (v) => v?.toUpperCase?.() ?? v },
              { key: "issued_at", label: "Issued" },
              { key: "due_at", label: "Due" },
              { key: "paid_at", label: "Paid" },
              { key: "notes", label: "Notes" }
            ],
            rows: invoices,
            empty: "No invoices found."
          }
        )
      ] })
    ] })
  ] });
}
export {
  Billing as default
};
