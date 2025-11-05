import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useCallback, useEffect, useMemo } from "react";
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
function ComplianceMatrix() {
  const [matrix, setMatrix] = useState({ frameworks: [], rules: [] });
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadMatrix = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/compliance-matrix/matrix`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setMatrix(data ?? { frameworks: [], rules: [] });
    } catch (err) {
      setError(err.message || "Failed to load compliance matrix");
    } finally {
      setLoading(false);
    }
  }, [token]);
  useEffect(() => {
    loadMatrix();
  }, [loadMatrix]);
  const filteredRules = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return matrix.rules;
    return matrix.rules.filter(
      (rule) => [rule.control_id, rule.title, rule.description, rule.category].filter(Boolean).some((value) => String(value).toLowerCase().includes(term))
    );
  }, [matrix.rules, search]);
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Compliance Matrix" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Explore Tenantra controls mapped to major regulatory frameworks including ISO 27001, NIST CSF, HIPAA, PCI-DSS, GDPR, and CIS." })
    ] }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsx(
        "input",
        {
          value: search,
          onChange: (e) => setSearch(e.target.value),
          placeholder: "Search controls...",
          className: "w-full max-w-md rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: loadMatrix, disabled: loading, children: loading ? "Refreshing..." : "Reload" })
    ] }) }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-8 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-8", children: [
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Frameworks" }),
        /* @__PURE__ */ jsx("div", { className: "grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3", children: matrix.frameworks.length === 0 ? /* @__PURE__ */ jsx("div", { className: "text-sm text-gray-500", children: "No frameworks configured." }) : matrix.frameworks.map((fw) => /* @__PURE__ */ jsxs("div", { className: "rounded-lg bg-white p-4 shadow", children: [
          /* @__PURE__ */ jsx("div", { className: "text-sm font-medium text-gray-900", children: fw.name }),
          /* @__PURE__ */ jsx("div", { className: "mt-1 text-xs text-gray-500", children: fw.code }),
          /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-gray-500", children: fw.description || "No description" }),
          fw.category && /* @__PURE__ */ jsxs("div", { className: "mt-2 text-xs text-gray-700", children: [
            "Category: ",
            fw.category
          ] })
        ] }, fw.id)) })
      ] }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Controls" }),
        /* @__PURE__ */ jsx(
          Table,
          {
            columns: [
              { key: "control_id", label: "Control" },
              { key: "title", label: "Title" },
              {
                key: "framework_ids",
                label: "Frameworks",
                render: (framework_ids) => framework_ids.map((fid) => matrix.frameworks.find((fw) => fw.id === fid)?.code || fid).join(", ") || "-"
              },
              { key: "category", label: "Category" },
              { key: "description", label: "Description" }
            ],
            rows: filteredRules,
            empty: "No controls match this query."
          }
        )
      ] })
    ] })
  ] });
}
export {
  ComplianceMatrix as default
};
