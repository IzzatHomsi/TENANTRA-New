import { jsxs, jsx } from "react/jsx-runtime";
import React, { useState, useCallback, useEffect } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { T as Table } from "./Table-CLWnewy9.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");
  const [sortBy, setSortBy] = useState("sent_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadNotifications = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/notifications`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setNotifications(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e.message || "Failed to load notifications.");
    } finally {
      setLoading(false);
    }
  }, [token]);
  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);
  const filteredNotifications = React.useMemo(() => {
    return notifications.filter(
      (notification) => JSON.stringify(notification).toLowerCase().includes(filter.toLowerCase())
    ).sort((a, b) => {
      if (a[sortBy] < b[sortBy]) return sortOrder === "asc" ? -1 : 1;
      if (a[sortBy] > b[sortBy]) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, [notifications, filter, sortBy, sortOrder]);
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };
  const columns = [
    { key: "title", label: "Title" },
    { key: "message", label: "Message" },
    { key: "sent_at", label: "Sent At" }
  ];
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Notifications" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "System, compliance, and workflow alerts land here for quick triage." })
    ] }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs(Card, { children: [
      /* @__PURE__ */ jsx("div", { className: "mb-4", children: /* @__PURE__ */ jsx(
        "input",
        {
          type: "text",
          value: filter,
          onChange: (e) => setFilter(e.target.value),
          className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          placeholder: "Filter notifications..."
        }
      ) }),
      /* @__PURE__ */ jsx(
        Table,
        {
          columns: columns.map((c) => ({ ...c, label: /* @__PURE__ */ jsxs("div", { onClick: () => handleSort(c.key), children: [
            c.label,
            " ",
            sortBy === c.key && (sortOrder === "asc" ? "▲" : "▼")
          ] }) })),
          rows: filteredNotifications,
          empty: "No notifications yet. New activity will surface here automatically."
        }
      )
    ] })
  ] });
}
export {
  Notifications as default
};
