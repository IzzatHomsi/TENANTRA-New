import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useEffect, useMemo } from "react";
import { a as useTheme, g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const API_BASE = getApiBase();
const buildGrafanaUrl = (base, dashUid, options = {}) => {
  const params = new URLSearchParams({
    orgId: 1,
    ...options
  });
  return `${base.replace(/\/$/, "")}/d/${encodeURIComponent(dashUid)}?${params.toString()}`;
};
function Metrics() {
  const { resolvedTheme } = useTheme();
  const [grafanaUrl, setGrafanaUrl] = useState("");
  const [dashUid, setDashUid] = useState("");
  const [dsUid, setDsUid] = useState("");
  const [panelIds, setPanelIds] = useState("2,4,6");
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/support/settings/public`);
        if (res.ok) {
          const j = await res.json();
          setGrafanaUrl(j["grafana.url"] || "");
          setDashUid(j["grafana.dashboard_uid"] || "");
          setDsUid(j["grafana.datasource_uid"] || "");
        }
      } catch {
      }
    })();
  }, []);
  const canEmbed = grafanaUrl && dashUid;
  const panelIdList = useMemo(() => panelIds.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n)), [panelIds]);
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Metrics" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Embedded Grafana dashboard and optional panels." })
    ] }),
    !canEmbed ? /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx("p", { className: "text-center text-gray-500", children: "Set Grafana URL and Dashboard UID in Admin Settings to render metrics here." }) }) : /* @__PURE__ */ jsxs("div", { className: "space-y-8", children: [
      /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(
        "iframe",
        {
          title: "Grafana Dashboard",
          src: buildGrafanaUrl(grafanaUrl, dashUid, { kiosk: "tv", theme: resolvedTheme === "dark" ? "dark" : "light", ...dsUid && { "var-datasource": dsUid } }),
          className: "h-[520px] w-full rounded-lg border-0"
        }
      ) }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Embed Individual Panels" }),
        /* @__PURE__ */ jsx(
          "input",
          {
            value: panelIds,
            onChange: (e) => setPanelIds(e.target.value),
            placeholder: "Panel IDs (comma-separated), e.g., 2,4,6",
            className: "w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          }
        ),
        /* @__PURE__ */ jsx("div", { className: "mt-6 grid grid-cols-1 gap-6 md:grid-cols-2", children: panelIdList.map((id) => /* @__PURE__ */ jsx("div", { className: "overflow-hidden rounded-lg shadow", children: /* @__PURE__ */ jsx(
          "iframe",
          {
            title: `Panel ${id}`,
            src: buildGrafanaUrl(grafanaUrl, dashUid, { theme: resolvedTheme === "dark" ? "dark" : "light", viewPanel: id, ...dsUid && { "var-datasource": dsUid } }),
            className: "h-[360px] w-full border-0"
          }
        ) }, id)) })
      ] })
    ] })
  ] });
}
export {
  Metrics as default
};
