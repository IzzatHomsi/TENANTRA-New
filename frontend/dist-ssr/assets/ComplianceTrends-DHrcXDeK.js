import { jsxs, jsx } from "react/jsx-runtime";
import "react";
import { C as Card } from "./Card-BYs02NaX.js";
const SUMMARY = [
  {
    title: "Overall Coverage",
    metric: "82%",
    hint: "Passing controls across all assets."
  },
  {
    title: "Open Failures",
    metric: "37",
    hint: "Failing checks not yet resolved."
  },
  {
    title: "30-Day Trend",
    metric: "+6%",
    hint: "Net improvement in pass rate."
  }
];
function ComplianceTrends() {
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Compliance Trends" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Track control coverage, failed checks by family, and drift over time. Scope respects tenant and RBAC filters." })
    ] }),
    /* @__PURE__ */ jsx("div", { className: "grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3", children: SUMMARY.map(({ title, metric, hint }) => /* @__PURE__ */ jsxs(Card, { children: [
      /* @__PURE__ */ jsx("div", { className: "text-4xl font-bold text-facebook-blue", children: metric }),
      /* @__PURE__ */ jsx("div", { className: "mt-2 text-lg font-medium text-gray-900", children: title }),
      /* @__PURE__ */ jsx("p", { className: "mt-1 text-sm text-gray-600", children: hint })
    ] }, title)) }),
    /* @__PURE__ */ jsx("div", { className: "mt-8 rounded-lg bg-blue-100 p-6 text-sm text-blue-800", children: /* @__PURE__ */ jsx("p", { children: "Ensure all data requests enforce tenant and role filters (RBAC) before exposing production metrics." }) })
  ] });
}
export {
  ComplianceTrends as default
};
