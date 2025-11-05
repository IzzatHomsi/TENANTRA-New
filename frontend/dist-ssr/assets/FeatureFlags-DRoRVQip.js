import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useCallback, useEffect } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import { u as useUIStore } from "./apiClient-Y8eZ7muQ.js";
import { f as fetchFeatureFlags } from "./features-DC5_-U-G.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
import "zustand";
import "zustand/middleware";
import "zod";
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
function FeatureFlags() {
  const { featureFlags, setFeatureFlags } = useUIStore();
  const [features, setFeatures] = useState(featureFlags || {});
  const [scope, setScope] = useState("tenant");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadFeatures = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchFeatureFlags(token);
      setFeatures(data || {});
      setFeatureFlags(data || {});
    } catch (e) {
      setError(e.message || "Failed to load features");
    } finally {
      setLoading(false);
    }
  }, [token, setFeatureFlags]);
  useEffect(() => {
    loadFeatures();
  }, [loadFeatures]);
  const saveFeatures = async () => {
    setSaving(true);
    setError("");
    try {
      const url = scope === "global" ? `${API_BASE}/admin/settings` : `${API_BASE}/admin/settings/tenant`;
      const res = await fetch(url, {
        method: "PUT",
        headers: authHeaders(token),
        body: JSON.stringify({ features })
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      setToast("Saved");
      setTimeout(() => setToast(""), 1500);
      loadFeatures();
    } catch (e) {
      setError(e.message || "Failed to save feature flags");
    } finally {
      setSaving(false);
    }
  };
  const toggleFeature = (key) => {
    setFeatures((prev) => ({ ...prev, [key]: !prev[key] }));
  };
  const featureKeys = Object.keys(features).sort();
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Feature Flags" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Manage platform feature visibility globally or per-tenant (overrides)." })
    ] }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    toast && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-green-100 p-4 text-green-700", children: toast }),
    /* @__PURE__ */ jsxs(Card, { children: [
      /* @__PURE__ */ jsxs("div", { className: "mb-4 flex items-center justify-between", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
          /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-gray-700", children: "Scope" }),
          /* @__PURE__ */ jsxs(
            "select",
            {
              value: scope,
              onChange: (e) => setScope(e.target.value),
              className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
              children: [
                /* @__PURE__ */ jsx("option", { value: "tenant", children: "Tenant" }),
                /* @__PURE__ */ jsx("option", { value: "global", children: "Global" })
              ]
            }
          )
        ] }),
        /* @__PURE__ */ jsx(Button, { onClick: saveFeatures, disabled: saving || loading, children: saving ? "Saving..." : "Save" })
      ] }),
      loading ? /* @__PURE__ */ jsx("div", { className: "py-12 text-center text-gray-500", children: "Loading..." }) : /* @__PURE__ */ jsx("ul", { className: "divide-y divide-gray-200", children: featureKeys.length === 0 ? /* @__PURE__ */ jsx("li", { className: "py-4 text-center text-sm text-gray-500", children: "No features discovered" }) : featureKeys.map((key) => /* @__PURE__ */ jsxs("li", { className: "flex items-center justify-between py-4", children: [
        /* @__PURE__ */ jsx("div", { className: "text-sm font-medium text-gray-900", children: key }),
        /* @__PURE__ */ jsxs("label", { className: "relative inline-flex cursor-pointer items-center", children: [
          /* @__PURE__ */ jsx(
            "input",
            {
              type: "checkbox",
              checked: !!features[key],
              onChange: () => toggleFeature(key),
              className: "sr-only peer"
            }
          ),
          /* @__PURE__ */ jsx("div", { className: "peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-facebook-blue peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300" }),
          /* @__PURE__ */ jsx("span", { className: "ml-3 text-sm font-medium text-gray-900", children: features[key] ? "Enabled" : "Disabled" })
        ] })
      ] }, key)) })
    ] })
  ] });
}
export {
  FeatureFlags as default
};
