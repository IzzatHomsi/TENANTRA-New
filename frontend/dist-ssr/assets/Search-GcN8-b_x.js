import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useMemo } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import { u as useAuth } from "../entry-server.js";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const NAV_CONFIG = [
  {
    type: "section",
    label: "Overview",
    children: [
      { type: "item", to: "/app/dashboard", label: "Dashboard" },
      { type: "item", to: "/app/profile", label: "My Profile" }
    ]
  },
  { type: "divider" },
  {
    type: "section",
    label: "Compliance",
    children: [
      // You said these pages exist in your project
      { type: "item", to: "/app/compliance-trends", label: "Compliance Trends" },
      { type: "item", to: "/app/notifications", label: "Notifications" },
      // Optional pages: enable them later by adding routes/pages
      {
        type: "item",
        to: "/app/compliance/results",
        label: "Compliance Results",
        enabled: ({ features }) => Boolean(features?.complianceResults)
      },
      {
        type: "item",
        to: "/app/notification-history",
        label: "Notification History",
        enabled: ({ features }) => Boolean(features?.notificationHistory)
      }
    ]
  },
  {
    type: "section",
    label: "Runtime Integrity",
    children: [
      { type: "item", to: "/app/process-monitoring", label: "Process Monitoring" },
      { type: "item", to: "/app/persistence", label: "Persistence" },
      {
        type: "item",
        to: "/app/threat-intel",
        label: "Threat Intelligence",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.threatIntel ?? true)
      }
    ]
  },
  {
    type: "section",
    label: "Assets & Scans",
    children: [
      {
        type: "item",
        to: "/app/assets",
        label: "Assets",
        enabled: ({ features }) => Boolean(features?.assets)
      },
      {
        type: "item",
        to: "/app/scan-schedules",
        label: "Scan Schedules",
        enabled: ({ features }) => Boolean(features?.scanSchedules)
      },
      {
        type: "item",
        to: "/app/reports",
        label: "Reports",
        enabled: ({ features }) => Boolean(features?.reports)
      },
      {
        type: "item",
        to: "/app/audit-logs",
        label: "Audit Logs",
        enabled: ({ features }) => Boolean(features?.auditLogs)
      }
    ]
  },
  { type: "divider" },
  {
    type: "section",
    label: "Administration",
    children: [
      // Only admins see Users/Tenants/Billing
      {
        type: "item",
        to: "/app/users",
        label: "Users",
        roles: ["admin", "administrator", "super_admin", "system_admin"]
      },
      {
        type: "item",
        to: "/app/tenants",
        label: "Tenants",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.tenants)
      },
      {
        type: "item",
        to: "/app/billing",
        label: "Billing",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.billing)
      },
      {
        type: "item",
        to: "/app/settings",
        label: "Settings",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.settings)
      }
    ]
  }
];
function getLocalFeatures() {
  return {
    // already existing pages:
    complianceResults: false,
    notificationHistory: false,
    // optional domains:
    assets: false,
    scanSchedules: false,
    reports: false,
    auditLogs: false,
    threatIntel: true,
    tenants: false,
    billing: false,
    settings: false
  };
}
function flattenNav(role, features) {
  const items = [];
  function walk(list) {
    for (const n of list) {
      if (n.type === "divider") continue;
      if (n.type === "section" && Array.isArray(n.children)) {
        walk(n.children);
      } else if (n.type === "item") {
        if (n.roles && n.roles.length && !n.roles.includes(role || "")) continue;
        const enabled = typeof n.enabled === "function" ? !!n.enabled({ role, features }) : n.enabled !== false;
        if (!enabled) continue;
        items.push({ to: n.to, label: n.label });
      }
    }
  }
  walk(NAV_CONFIG);
  return items;
}
function Search() {
  const navigate = useNavigate();
  const { search } = useLocation();
  const params = new URLSearchParams(search);
  const [q, setQ] = useState(params.get("q") || "");
  const { role } = useAuth();
  const features = getLocalFeatures();
  const items = useMemo(() => flattenNav(role, features), [role, features]);
  const filtered = useMemo(() => {
    const s = (q || "").toLowerCase();
    if (!s) return items;
    return items.filter((i) => String(i.label || "").toLowerCase().includes(s));
  }, [q, items]);
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Search" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Find pages and jump quickly." })
    ] }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsxs("div", { className: "flex space-x-4", children: [
      /* @__PURE__ */ jsx(
        "input",
        {
          autoFocus: true,
          value: q,
          onChange: (e) => setQ(e.target.value),
          placeholder: "Type to filter...",
          className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: () => {
        if (filtered[0]) navigate(filtered[0].to);
      }, children: "Go" })
    ] }) }),
    /* @__PURE__ */ jsx("div", { className: "space-y-4", children: filtered.length > 0 ? filtered.map((i) => /* @__PURE__ */ jsx(Card, { className: "hover:shadow-lg", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("div", { className: "font-medium text-gray-900", children: i.label }),
        /* @__PURE__ */ jsx("div", { className: "text-sm text-gray-500", children: i.to })
      ] }),
      /* @__PURE__ */ jsx(Button, { variant: "outline", onClick: () => navigate(i.to), children: "Open" })
    ] }) }, i.to)) : /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx("p", { className: "text-center text-gray-500", children: "No matches." }) }) })
  ] });
}
export {
  Search as default
};
