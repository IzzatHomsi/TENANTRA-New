import { jsxs, jsx } from "react/jsx-runtime";
import "react";
import { C as Card } from "./Card-BYs02NaX.js";
function ObservabilitySetup() {
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsx("header", { className: "mb-8", children: /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Observability Setup" }) }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-6", children: [
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Grafana Connectivity" }),
        /* @__PURE__ */ jsxs("ol", { className: "list-decimal space-y-2 pl-5 text-gray-700", children: [
          /* @__PURE__ */ jsxs("li", { children: [
            "Go to Admin Settings → Branding and set ",
            /* @__PURE__ */ jsx("code", { children: "grafana.url" }),
            " (e.g., http://localhost:3000). Save."
          ] }),
          /* @__PURE__ */ jsxs("li", { children: [
            "If Grafana requires auth, set backend env vars ",
            /* @__PURE__ */ jsx("code", { children: "GRAFANA_USER" }),
            " and ",
            /* @__PURE__ */ jsx("code", { children: "GRAFANA_PASS" }),
            ", then restart backend."
          ] }),
          /* @__PURE__ */ jsx("li", { children: "Use Admin Settings → Observability tab to Recheck health, validate a Dashboard UID (e.g., tenantra-overview), Datasource UID, and Slug." })
        ] })
      ] }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Prometheus" }),
        /* @__PURE__ */ jsxs("ul", { className: "list-disc space-y-2 pl-5 text-gray-700", children: [
          /* @__PURE__ */ jsx("li", { children: "Ensure Prometheus is running (compose override: docker-compose.override.observability.yml)." }),
          /* @__PURE__ */ jsxs("li", { children: [
            "Scrape Tenantra backend metrics endpoint at ",
            /* @__PURE__ */ jsx("code", { children: "http://backend:5000/metrics" }),
            " or via Nginx if exposed."
          ] })
        ] })
      ] }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Common Issues" }),
        /* @__PURE__ */ jsxs("ul", { className: "list-disc space-y-2 pl-5 text-gray-700", children: [
          /* @__PURE__ */ jsx("li", { children: '"grafana.url not configured": set it in Branding and Save.' }),
          /* @__PURE__ */ jsxs("li", { children: [
            "401/403 from Grafana: set ",
            /* @__PURE__ */ jsx("code", { children: "GRAFANA_USER" }),
            "/",
            /* @__PURE__ */ jsx("code", { children: "GRAFANA_PASS" }),
            "."
          ] }),
          /* @__PURE__ */ jsx("li", { children: "Network access: ensure containers share the same Docker network (core)." })
        ] })
      ] })
    ] })
  ] });
}
export {
  ObservabilitySetup as default
};
