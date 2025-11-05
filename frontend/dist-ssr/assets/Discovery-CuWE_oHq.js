import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { g as getApiBase, u as useAuth } from "../entry-server.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { u as useUIStore } from "./apiClient-Y8eZ7muQ.js";
import { f as fetchTenants } from "./tenants-Cz2KWSMQ.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
import "zustand";
import "zustand/middleware";
import "zod";
const API_BASE$2 = getApiBase();
const authHeaders$2 = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
function RunScan() {
  const [cidr, setCidr] = useState("");
  const [hosts, setHosts] = useState("");
  const [ports, setPorts] = useState("22,80,443");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const run = async () => {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const targetList = [];
      const parsedPorts = ports.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n) && n > 0 && n < 65536);
      if (cidr.trim()) {
        targetList.push({ host: cidr.trim(), ports: parsedPorts });
      }
      const hostList = hosts.split(/[\s,]+/).map((s) => s.trim()).filter(Boolean);
      for (const h of hostList) {
        targetList.push({ host: h, ports: parsedPorts });
      }
      if (targetList.length === 0) {
        setError("Provide a CIDR or at least one host.");
        setBusy(false);
        return;
      }
      const res = await fetch(`${API_BASE$2}/admin/network/port-scan`, {
        method: "POST",
        headers: authHeaders$2(token),
        body: JSON.stringify({ targets: targetList })
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e?.message || "Discovery failed");
    } finally {
      setBusy(false);
    }
  };
  return /* @__PURE__ */ jsxs(Card, { children: [
    /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Run Discovery Scan" }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "CIDR (optional)" }),
        /* @__PURE__ */ jsx(
          "input",
          {
            value: cidr,
            onChange: (e) => setCidr(e.target.value),
            placeholder: "10.0.0.0/24",
            className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        )
      ] }),
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Hosts (one per line or comma-separated)" }),
        /* @__PURE__ */ jsx(
          "textarea",
          {
            rows: 6,
            value: hosts,
            onChange: (e) => setHosts(e.target.value),
            placeholder: "10.0.0.5\nexample.local",
            className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        )
      ] }),
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Ports" }),
        /* @__PURE__ */ jsx(
          "input",
          {
            value: ports,
            onChange: (e) => setPorts(e.target.value),
            placeholder: "22,80,443",
            className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        )
      ] }),
      /* @__PURE__ */ jsx(Button, { onClick: run, disabled: busy, children: busy ? "Scanning..." : "Run Discovery" })
    ] }),
    result && /* @__PURE__ */ jsxs("div", { className: "mt-6", children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-medium text-gray-900", children: "Results" }),
      /* @__PURE__ */ jsxs("div", { className: "mt-4 space-y-2", children: [
        Array.isArray(result.findings) && result.findings.length ? /* @__PURE__ */ jsx("ul", { className: "space-y-2", children: result.findings.slice(0, 20).map((f, i) => /* @__PURE__ */ jsx("li", { className: "rounded-md bg-gray-100 p-3", children: /* @__PURE__ */ jsx("pre", { className: "text-sm", children: JSON.stringify(f, null, 2) }) }, i)) }) : /* @__PURE__ */ jsx("div", { className: "text-sm text-gray-500", children: "No findings returned." }),
        /* @__PURE__ */ jsxs("details", { className: "mt-4", children: [
          /* @__PURE__ */ jsx("summary", { className: "cursor-pointer text-sm text-gray-600", children: "Raw JSON" }),
          /* @__PURE__ */ jsx("pre", { className: "mt-2 max-h-72 overflow-auto rounded bg-gray-900 p-2 text-xs text-white", children: JSON.stringify(result, null, 2) })
        ] })
      ] })
    ] })
  ] });
}
const API_BASE$1 = getApiBase();
const authHeaders$1 = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
function CreateSchedule({ isAdmin }) {
  const [cron, setCron] = useState("*/30 * * * *");
  const [schedMsg, setSchedMsg] = useState("");
  const [error, setError] = useState("");
  const [agents, setAgents] = useState([]);
  const [tenantId, setTenantId] = useState("");
  const [agentId, setAgentId] = useState("");
  const [targets, setTargets] = useState([]);
  const { tenants } = useUIStore();
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  useEffect(() => {
    (async () => {
      if (!isAdmin) return;
      if (tenants.length > 0) return;
      try {
        await fetchTenants(token);
      } catch {
      }
    })();
  }, [isAdmin, token, tenants.length]);
  useEffect(() => {
    (async () => {
      if (!isAdmin) return;
      try {
        const qs = tenantId ? `?tenant_id=${tenantId}` : "";
        const res = await fetch(`${API_BASE$1}/admin/agents${qs}`, { headers: authHeaders$1(token) });
        if (res.ok) {
          setAgents(await res.json());
        }
      } catch {
        setAgents([]);
      }
    })();
  }, [isAdmin, token, tenantId]);
  const createSchedule = async () => {
    setSchedMsg("");
    setError("");
    if (!targets.length) {
      setError("Provide a CIDR or at least one host.");
      return;
    }
    try {
      let modules = await fetch(`${API_BASE$1}/modules/`, { headers: authHeaders$1(token) }).then((res) => res.json());
      let mod = (modules || []).find((m) => (m.external_id || "").toLowerCase() === "port-scan" || /port\s*scan/i.test(m.name || ""));
      if (!mod) {
        try {
          await fetch(`${API_BASE$1}/admin/modules/create-port-scan`, { method: "POST", headers: authHeaders$1(token) });
        } catch {
        }
        modules = await fetch(`${API_BASE$1}/modules/`, { headers: authHeaders$1(token) }).then((res) => res.json());
        mod = (modules || []).find((m) => (m.external_id || "").toLowerCase() === "port-scan" || /port\s*scan/i.test(m.name || ""));
      }
      if (!mod) {
        setError("Port Scan module not available. Ask an admin to seed modules.");
        return;
      }
      const payload = { module_id: mod.id, cron_expr: cron.trim() || "*/30 * * * *", parameters: { targets } };
      if (isAdmin && tenantId) {
        payload.tenant_id = Number(tenantId);
      }
      if (agentId) {
        const parsed = Number(agentId);
        if (!isNaN(parsed) && parsed > 0) {
          payload.agent_id = parsed;
        }
      }
      await fetch(`${API_BASE$1}/schedules`, { method: "POST", headers: authHeaders$1(token), body: JSON.stringify(payload) });
      setSchedMsg("Schedule created. View under Module Catalog → Schedules or Scan Orchestration.");
      setTimeout(() => setSchedMsg(""), 2600);
    } catch (e) {
      setError(e?.message || "Failed to create schedule");
    }
  };
  return /* @__PURE__ */ jsxs(Card, { children: [
    /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Create Recurring Schedule" }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    schedMsg && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-green-100 p-4 text-green-700", children: schedMsg }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
      isAdmin && /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-4 md:grid-cols-2", children: [
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Tenant (admin)" }),
          /* @__PURE__ */ jsxs(
            "select",
            {
              value: tenantId,
              onChange: (e) => setTenantId(e.target.value),
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
              children: [
                /* @__PURE__ */ jsx("option", { value: "", children: "Current tenant" }),
                tenants.map((t) => /* @__PURE__ */ jsx("option", { value: t.id, children: t.name }, t.id))
              ]
            }
          )
        ] }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Agent (optional)" }),
          /* @__PURE__ */ jsxs(
            "select",
            {
              value: agentId,
              onChange: (e) => setAgentId(e.target.value),
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
              children: [
                /* @__PURE__ */ jsx("option", { value: "", children: "Unassigned" }),
                agents.map((a) => /* @__PURE__ */ jsxs("option", { value: a.id, children: [
                  a.name,
                  " (#",
                  a.id,
                  ")"
                ] }, a.id))
              ]
            }
          )
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Cron expression" }),
        /* @__PURE__ */ jsx(
          "input",
          {
            value: cron,
            onChange: (e) => setCron(e.target.value),
            placeholder: "*/30 * * * *",
            className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        )
      ] }),
      /* @__PURE__ */ jsx(Button, { onClick: createSchedule, children: "Save Schedule" })
    ] })
  ] });
}
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
function CreateBulkSchedules({ isAdmin }) {
  const [bulkText, setBulkText] = useState("");
  const [bulkMsg, setBulkMsg] = useState("");
  const [error, setError] = useState("");
  const [ports, setPorts] = useState("22,80,443");
  const [cron, setCron] = useState("*/30 * * * *");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const createBulkSchedules = async () => {
    setBulkMsg("");
    setError("");
    if (!isAdmin) {
      setError("Admin only");
      return;
    }
    const lines = bulkText.split(/\n+/).map((s) => s.trim()).filter(Boolean);
    if (!lines.length) {
      setError("Provide one or more lines: tenant_id=cidr1;cidr2");
      return;
    }
    try {
      let modules = await fetch(`${API_BASE}/modules/`, { headers: authHeaders(token) }).then((res) => res.json());
      let mod = (modules || []).find((m) => (m.external_id || "").toLowerCase() === "port-scan" || /port\s*scan/i.test(m.name || ""));
      if (!mod) {
        try {
          await fetch(`${API_BASE}/admin/modules/create-port-scan`, { method: "POST", headers: authHeaders(token) });
        } catch {
        }
        modules = await fetch(`${API_BASE}/modules/`, { headers: authHeaders(token) }).then((res) => res.json());
        mod = (modules || []).find((m) => (m.external_id || "").toLowerCase() === "port-scan" || /port\s*scan/i.test(m.name || ""));
      }
      if (!mod) {
        setError("Port Scan module not available.");
        return;
      }
      const parsedPorts = ports.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n) && n > 0 && n < 65536);
      let created = 0, errors = 0;
      for (const line of lines) {
        const [lhs, rangesRaw] = line.split("=");
        const [tidPart, aidPart] = (lhs || "").split(":");
        const tid = Number((tidPart || "").trim());
        const aid = aidPart ? Number(aidPart.trim()) : null;
        if (!tid || !rangesRaw) {
          errors++;
          continue;
        }
        const ranges = rangesRaw.split(/;| |\s+/).map((s) => s.trim()).filter(Boolean);
        if (!ranges.length) {
          errors++;
          continue;
        }
        const targets = ranges.map((r) => ({ host: r, ports: parsedPorts }));
        try {
          const payload = { module_id: mod.id, cron_expr: cron.trim() || "*/30 * * * *", tenant_id: tid, parameters: { targets } };
          if (aid && !isNaN(aid) && aid > 0) {
            payload.agent_id = aid;
          }
          await fetch(`${API_BASE}/schedules`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
          created++;
        } catch {
          errors++;
        }
      }
      setBulkMsg(`Created ${created} schedules${errors ? `, ${errors} failed` : ""}`);
      setTimeout(() => setBulkMsg(""), 3e3);
    } catch (e) {
      setError(e?.message || "Bulk creation failed");
    }
  };
  if (!isAdmin) {
    return null;
  }
  return /* @__PURE__ */ jsxs(Card, { children: [
    /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Bulk Per-Tenant Schedules" }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    bulkMsg && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-green-100 p-4 text-green-700", children: bulkMsg }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Tenant Schedules (one per line: tenant_id=cidr1;cidr2)" }),
        /* @__PURE__ */ jsx(
          "textarea",
          {
            rows: 6,
            value: bulkText,
            onChange: (e) => setBulkText(e.target.value),
            placeholder: "1=10.0.1.0/24;10.0.2.0/24\n2=192.168.1.0/24",
            className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        )
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-4 md:grid-cols-2", children: [
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Ports" }),
          /* @__PURE__ */ jsx(
            "input",
            {
              value: ports,
              onChange: (e) => setPorts(e.target.value),
              placeholder: "22,80,443",
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            }
          )
        ] }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Cron expression" }),
          /* @__PURE__ */ jsx(
            "input",
            {
              value: cron,
              onChange: (e) => setCron(e.target.value),
              placeholder: "*/30 * * * *",
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            }
          )
        ] })
      ] }),
      /* @__PURE__ */ jsx(Button, { onClick: createBulkSchedules, children: "Create Schedules" })
    ] })
  ] });
}
function Discovery() {
  const { role } = useAuth();
  const isAdmin = role === "admin" || role === "super_admin";
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Network Discovery" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Scan one or more hosts/ranges for open TCP ports and basic service signals." })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-8", children: [
      /* @__PURE__ */ jsx(RunScan, {}),
      /* @__PURE__ */ jsx(CreateSchedule, { isAdmin }),
      /* @__PURE__ */ jsx(CreateBulkSchedules, { isAdmin })
    ] })
  ] });
}
export {
  Discovery as default
};
