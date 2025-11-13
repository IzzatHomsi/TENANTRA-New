import { jsxs, jsx, Fragment } from "react/jsx-runtime";
import "react";
import { C as Card } from "./Card-BYs02NaX.js";
const FAQ_DATA = [
  {
    question: "Where do I start?",
    answer: "Bring the stack up from `docker/` with `docker compose up -d`. Frontend runs on `http://localhost:8080`, backend on `http://localhost:5000`. Configure the default admin credentials via `TENANTRA_ADMIN_PASSWORD` (see `.env.example`)."
  },
  {
    question: "Configuring Observability",
    answer: /* @__PURE__ */ jsxs("ul", { className: "list-disc space-y-2 pl-5", children: [
      /* @__PURE__ */ jsx("li", { children: "Set `grafana.url` under Admin Settings → Branding and Save." }),
      /* @__PURE__ */ jsx("li", { children: "If required, set backend env `GRAFANA_USER` and `GRAFANA_PASS` and restart backend." }),
      /* @__PURE__ */ jsx("li", { children: "Use Observability tab to verify health, dashboard UID, datasource UID, and slug." })
    ] })
  },
  {
    question: "Networking — Port Scan",
    answer: /* @__PURE__ */ jsxs(Fragment, { children: [
      /* @__PURE__ */ jsx("p", { children: "Use Module Catalog → Quick Action to run a TCP port scan. Backend admin API:" }),
      /* @__PURE__ */ jsx("pre", { className: "mt-2 overflow-auto rounded-lg bg-gray-800 p-4 text-sm text-white", children: /* @__PURE__ */ jsx("code", { children: `POST /api/admin/network/port-scan
{
  "host": "10.0.0.5",
  "ports": [22,80,443]
}` }) })
    ] })
  },
  {
    question: "Control Menu",
    answer: "Run `tenantra_control_menu.bat`. Actions stream logs live and show status badges. Use [6] to rebuild, [2]/[3] to start, [5] to clean volumes."
  },
  {
    question: "Cleanup",
    answer: "Preview: `tools/cleanup_report.ps1`. Apply: `tools/cleanup_report.ps1 -Apply`."
  }
];
function FAQ() {
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsx("header", { className: "mb-8", children: /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Frequently Asked Questions (FAQ)" }) }),
    /* @__PURE__ */ jsx("div", { className: "space-y-6", children: FAQ_DATA.map((item, index) => /* @__PURE__ */ jsxs(Card, { children: [
      /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: item.question }),
      /* @__PURE__ */ jsx("div", { className: "text-sm text-gray-700", children: item.answer })
    ] }, index)) })
  ] });
}
export {
  FAQ as default
};
