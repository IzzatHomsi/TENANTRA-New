import { jsx, jsxs } from "react/jsx-runtime";
import { useState, useCallback, useEffect } from "react";
import { a as useTheme, g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const paths = {
  bolt: "M13 3L4 14h7l-1 7 9-11h-7l1-7z",
  clock: "M12 8v5l4 2m5-3a9 9 0 11-18 0 9 9 0 0118 0z",
  shield: "M12 22s8-4 8-10V6l-8-4-8 4v6c0 6 8 10 8 10z",
  graph: "M4 19h16M7 12l3 3 7-7",
  search: "M21 21l-4.35-4.35M10 18a8 8 0 100-16 8 8 0 000 16z",
  user: "M12 14a5 5 0 100-10 5 5 0 000 10zm7 8a7 7 0 10-14 0h14z"
};
function Icon({ name, size = 18, className = "", stroke = 2 }) {
  const d = paths[name] || paths.graph;
  return /* @__PURE__ */ jsx(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      strokeWidth: stroke,
      strokeLinecap: "round",
      strokeLinejoin: "round",
      width: size,
      height: size,
      className,
      children: /* @__PURE__ */ jsx("path", { d })
    }
  );
}
const EMPTY = { value: "-", hint: "", icon: "graph" };
const REFRESH_INTERVAL = parseInt("15000", 10);
const fetchApiLatency = async () => {
  try {
    const t0 = performance.now();
    await fetch(`${getApiBase()}/health`, { cache: "no-store" });
    const t1 = performance.now();
    const ms = Math.max(1, Math.round(t1 - t0));
    return { value: `${ms}ms`, hint: "API ping latency", icon: "clock" };
  } catch {
    return { value: "n/a", hint: "API not reachable", icon: "clock" };
  }
};
const fetchAuthStatus = async () => {
  try {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const res = await fetch(`${getApiBase()}/auth/me`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
    return { value: res.ok ? "OK" : String(res.status), hint: "Auth session status", icon: "shield" };
  } catch {
    return { value: "n/a", hint: "Auth check failed", icon: "shield" };
  }
};
const fetchGrafanaHealth = async () => {
  try {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const res = await fetch(`/api/admin/observability/grafana/health`, { cache: "no-store", headers: token ? { Authorization: `Bearer ${token}` } : {} });
    return { value: res.ok ? "OK" : String(res.status), hint: "Grafana /api/health via backend", icon: "bolt" };
  } catch {
    return { value: "n/a", hint: "Grafana not reachable", icon: "bolt" };
  }
};
function Dashboard() {
  const { resolvedTheme } = useTheme();
  const [grafanaUrl, setGrafanaUrl] = useState("");
  const [dashUid, setDashUid] = useState("");
  const [dsUid, setDsUid] = useState("");
  const [cards, setCards] = useState({
    apiLatency: { ...EMPTY, hint: "API ping latency" },
    authStatus: { ...EMPTY, hint: "Auth session status", icon: "shield" },
    grafana: { ...EMPTY, hint: "Grafana health", icon: "bolt" }
  });
  const refreshAll = useCallback(async () => {
    const [apiLatency, authStatus, grafana] = await Promise.all([
      fetchApiLatency(),
      fetchAuthStatus(),
      fetchGrafanaHealth()
    ]);
    setCards({ apiLatency, authStatus, grafana });
  }, []);
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${getApiBase()}/support/settings/public`);
        if (res.ok) {
          const j = await res.json();
          setGrafanaUrl(j["grafana.url"] || "");
          setDashUid(j["grafana.dashboard_uid"] || "");
          setDsUid(j["grafana.datasource_uid"] || "");
        }
      } catch {
      }
    })();
    refreshAll();
    const intervalId = setInterval(refreshAll, REFRESH_INTERVAL);
    return () => clearInterval(intervalId);
  }, [refreshAll]);
  const canEmbed = grafanaUrl && dashUid;
  const iframeSrc = canEmbed ? `${grafanaUrl.replace(/\/$/, "")}/d/${encodeURIComponent(dashUid)}?orgId=1&kiosk=tv&theme=${resolvedTheme === "dark" ? "dark" : "light"}${dsUid ? `&var-datasource=${encodeURIComponent(dsUid)}` : ""}` : "";
  return /* @__PURE__ */ jsxs("div", { className: "space-y-6 bg-facebook-gray p-6", children: [
    /* @__PURE__ */ jsxs("header", { className: "border-b border-gray-200 pb-4", children: [
      /* @__PURE__ */ jsx("div", { className: "text-xs uppercase tracking-wide text-gray-500", children: "Overview" }),
      /* @__PURE__ */ jsx("h1", { className: "mt-1 text-2xl font-bold text-gray-900", children: "Operations Dashboard" }),
      /* @__PURE__ */ jsx("p", { className: "mt-1 text-sm text-gray-600", children: "Welcome to Tenantra. Your tenant health snapshot updates as data sources sync and telemetry streams in." })
    ] }),
    canEmbed ? /* @__PURE__ */ jsx(Card, { padded: false, className: "overflow-hidden rounded-lg shadow-lg", children: /* @__PURE__ */ jsx("iframe", { title: "Grafana Dashboard", src: iframeSrc, className: "w-full h-[520px] border-0" }) }) : /* @__PURE__ */ jsx(Card, { className: "border-yellow-400 bg-yellow-100 text-yellow-800", children: /* @__PURE__ */ jsx("div", { className: "text-sm", children: "To view live metrics, set Grafana URL and Dashboard UID in Admin Settings. Optionally set Datasource UID." }) }),
    /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3", children: [
      /* @__PURE__ */ jsx(Card, { className: "bg-facebook-white rounded-lg shadow-lg", children: /* @__PURE__ */ jsxs("div", { className: "flex items-start gap-4", children: [
        /* @__PURE__ */ jsx("div", { className: "rounded-full bg-blue-100 p-3 text-facebook-blue", children: /* @__PURE__ */ jsx(Icon, { name: "clock" }) }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("div", { className: "text-3xl font-bold text-gray-900", children: cards.apiLatency.value }),
          /* @__PURE__ */ jsx("div", { className: "mt-1 text-base font-medium text-gray-700", children: "API Latency" }),
          /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-500", children: cards.apiLatency.hint })
        ] })
      ] }) }),
      /* @__PURE__ */ jsx(Card, { className: "bg-facebook-white rounded-lg shadow-lg", children: /* @__PURE__ */ jsxs("div", { className: "flex items-start gap-4", children: [
        /* @__PURE__ */ jsx("div", { className: "rounded-full bg-green-100 p-3 text-green-600", children: /* @__PURE__ */ jsx(Icon, { name: "shield" }) }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("div", { className: "text-3xl font-bold text-gray-900", children: cards.authStatus.value }),
          /* @__PURE__ */ jsx("div", { className: "mt-1 text-base font-medium text-gray-700", children: "Auth Status" }),
          /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-500", children: cards.authStatus.hint })
        ] })
      ] }) }),
      /* @__PURE__ */ jsx(Card, { className: "bg-facebook-white rounded-lg shadow-lg", children: /* @__PURE__ */ jsxs("div", { className: "flex items-start gap-4", children: [
        /* @__PURE__ */ jsx("div", { className: "rounded-full bg-purple-100 p-3 text-purple-600", children: /* @__PURE__ */ jsx(Icon, { name: "bolt" }) }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("div", { className: "text-3xl font-bold text-gray-900", children: cards.grafana.value }),
          /* @__PURE__ */ jsx("div", { className: "mt-1 text-base font-medium text-gray-700", children: "Grafana" }),
          /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-500", children: cards.grafana.hint })
        ] })
      ] }) })
    ] })
  ] });
}
export {
  Dashboard as default
};
