import { jsx, jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
const EVENT_LABELS = {
  scan_failed: "Scan Failed",
  compliance_violation: "Compliance Violation",
  agent_offline: "Agent Offline",
  threshold_breach: "Threshold Breach"
};
function AlertSettings() {
  const [channels, setChannels] = useState({ email: true, webhook: false });
  const [events, setEvents] = useState({
    scan_failed: true,
    compliance_violation: true,
    agent_offline: true,
    threshold_breach: false
  });
  const [digest, setDigest] = useState("immediate");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  useEffect(() => {
    const fetchPrefs = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(`${API_BASE}/notification-prefs`, { headers: authHeaders(token) });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        if (data) {
          setChannels(data.channels || { email: true, webhook: false });
          setEvents(data.events || { scan_failed: true, compliance_violation: true, agent_offline: true, threshold_breach: false });
          setDigest(data.digest || "immediate");
        }
      } catch (e) {
        setError(e.message || "Failed to load preferences");
      } finally {
        setLoading(false);
      }
    };
    fetchPrefs();
  }, [token]);
  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/notification-prefs`, {
        method: "PUT",
        headers: authHeaders(token),
        body: JSON.stringify({ channels, events, digest })
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
    } catch (e) {
      setError(e.message || "Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };
  if (loading) {
    return /* @__PURE__ */ jsx("div", { className: "flex h-full items-center justify-center bg-facebook-gray", children: /* @__PURE__ */ jsx("p", { children: "Loading alert settings..." }) });
  }
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Alert Settings" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Manage notification channels, event triggers, and digest preferences." })
    ] }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs(Card, { className: "space-y-8", children: [
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium leading-6 text-gray-900", children: "Channels" }),
        /* @__PURE__ */ jsxs("div", { className: "mt-4 space-y-2", children: [
          /* @__PURE__ */ jsxs("label", { className: "flex items-center", children: [
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "checkbox",
                checked: channels.email,
                onChange: (e) => setChannels({ ...channels, email: e.target.checked }),
                className: "h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
              }
            ),
            /* @__PURE__ */ jsx("span", { className: "ml-2 text-sm text-gray-700", children: "Email" })
          ] }),
          /* @__PURE__ */ jsxs("label", { className: "flex items-center", children: [
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "checkbox",
                checked: channels.webhook,
                onChange: (e) => setChannels({ ...channels, webhook: e.target.checked }),
                className: "h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
              }
            ),
            /* @__PURE__ */ jsx("span", { className: "ml-2 text-sm text-gray-700", children: "Webhook" })
          ] })
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium leading-6 text-gray-900", children: "Events" }),
        /* @__PURE__ */ jsx("div", { className: "mt-4 grid grid-cols-1 gap-4 md:grid-cols-2", children: Object.keys(events).map((key) => /* @__PURE__ */ jsxs("label", { className: "flex items-center", children: [
          /* @__PURE__ */ jsx(
            "input",
            {
              type: "checkbox",
              checked: events[key],
              onChange: (e) => setEvents({ ...events, [key]: e.target.checked }),
              className: "h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
            }
          ),
          /* @__PURE__ */ jsx("span", { className: "ml-2 text-sm text-gray-700", children: EVENT_LABELS[key] || key.replace(/_/g, " ") })
        ] }, key)) })
      ] }),
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium leading-6 text-gray-900", children: "Digest" }),
        /* @__PURE__ */ jsxs(
          "select",
          {
            value: digest,
            onChange: (e) => setDigest(e.target.value),
            className: "mt-4 block w-full max-w-xs rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
            children: [
              /* @__PURE__ */ jsx("option", { value: "immediate", children: "Immediate" }),
              /* @__PURE__ */ jsx("option", { value: "hourly", children: "Hourly" }),
              /* @__PURE__ */ jsx("option", { value: "daily", children: "Daily" })
            ]
          }
        )
      ] }),
      /* @__PURE__ */ jsx("div", { className: "flex justify-end", children: /* @__PURE__ */ jsx(Button, { onClick: handleSave, disabled: saving, children: saving ? "Saving..." : "Save Preferences" }) })
    ] })
  ] });
}
export {
  AlertSettings as default
};
