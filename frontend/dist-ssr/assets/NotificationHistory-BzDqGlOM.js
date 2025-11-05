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
function NotificationHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({
    channel: "",
    recipient: "",
    limit: 50
  });
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const qs = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          qs.set(key, value);
        }
      });
      const res = await fetch(`${API_BASE}/notification-history?${qs.toString()}`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load notification history");
    } finally {
      setLoading(false);
    }
  }, [token, filters]);
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };
  const columns = [
    { key: "sent_at", label: "Sent" },
    { key: "channel", label: "Channel" },
    { key: "recipient", label: "Recipient" },
    { key: "subject", label: "Subject" },
    { key: "status", label: "Status" },
    { key: "error", label: "Error", render: (v) => v ? /* @__PURE__ */ jsx("span", { className: "text-red-600", children: v }) : "-" }
  ];
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Notification History" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Review alerts and messages sent to tenant stakeholders with filters by channel and recipient." })
    ] }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
      /* @__PURE__ */ jsx(
        "input",
        {
          name: "channel",
          value: filters.channel,
          onChange: handleFilterChange,
          placeholder: "Channel (email, sms, webhook)",
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      ),
      /* @__PURE__ */ jsx(
        "input",
        {
          name: "recipient",
          value: filters.recipient,
          onChange: handleFilterChange,
          placeholder: "Recipient",
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      ),
      /* @__PURE__ */ jsx(
        "select",
        {
          name: "limit",
          value: filters.limit,
          onChange: handleFilterChange,
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [50, 100, 200, 500, 1e3].map((n) => /* @__PURE__ */ jsxs("option", { value: n, children: [
            n,
            " rows"
          ] }, n))
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: loadHistory, disabled: loading, children: loading ? "Refreshing..." : "Apply" })
    ] }) }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-8 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(Table, { columns, rows: history, empty: "No notifications found." }) })
  ] });
}
export {
  NotificationHistory as default
};
