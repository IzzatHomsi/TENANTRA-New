import { jsx, jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const API_BASE = getApiBase();
function Onboarding() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [mode, setMode] = useState("single");
  const [tenantName, setTenantName] = useState("");
  const [tenantSlug, setTenantSlug] = useState("");
  const [msg, setMsg] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/admin/settings`, { headers });
        if (res.ok) {
          const items = await res.json();
          const map = Object.fromEntries(items.map((x) => [x.key, x.value]));
          if (map["tenant.mode"]) setMode(map["tenant.mode"]);
          if (map["onboarding.done"]) {
            window.location.assign("/app/dashboard");
            return;
          }
        }
      } catch {
      }
      setLoading(false);
    })();
  }, [headers]);
  async function handleSave() {
    setSaving(true);
    setMsg("");
    try {
      const body = { "tenant.mode": mode, "onboarding.done": true };
      const s = await fetch(`${API_BASE}/admin/settings`, { method: "PUT", headers, body: JSON.stringify(body) });
      if (!s.ok) throw new Error(`HTTP ${s.status}`);
      if (mode === "single") {
        const name = tenantName.trim() || "Default Tenant";
        const slug = tenantSlug.trim() || "default";
        try {
          await fetch(`${API_BASE}/admin/tenants`, { method: "POST", headers, body: JSON.stringify({ name, slug }) });
        } catch {
        }
      }
      setMsg("Onboarding complete. Redirecting...");
      setTimeout(() => window.location.assign("/app/dashboard"), 700);
    } catch (e) {
      setMsg(String(e?.message || e || "Failed to save"));
    } finally {
      setSaving(false);
    }
  }
  if (loading) return /* @__PURE__ */ jsx("div", { className: "p-8 text-center", children: "Loading..." });
  return /* @__PURE__ */ jsx("div", { className: "flex min-h-screen items-center justify-center bg-facebook-gray p-8", children: /* @__PURE__ */ jsxs(Card, { className: "w-full max-w-2xl", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8 text-center", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Tenantra Setup" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Choose tenant mode and create your first tenant if needed." })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-6", children: [
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Mode" }),
        /* @__PURE__ */ jsxs("div", { className: "flex space-x-4", children: [
          /* @__PURE__ */ jsxs("label", { className: "flex items-center", children: [
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "radio",
                name: "mode",
                checked: mode === "single",
                onChange: () => setMode("single"),
                className: "h-4 w-4 border-gray-300 text-facebook-blue focus:ring-facebook-blue"
              }
            ),
            /* @__PURE__ */ jsx("span", { className: "ml-2 text-sm text-gray-700", children: "Single tenant" })
          ] }),
          /* @__PURE__ */ jsxs("label", { className: "flex items-center", children: [
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "radio",
                name: "mode",
                checked: mode === "multi",
                onChange: () => setMode("multi"),
                className: "h-4 w-4 border-gray-300 text-facebook-blue focus:ring-facebook-blue"
              }
            ),
            /* @__PURE__ */ jsx("span", { className: "ml-2 text-sm text-gray-700", children: "Multi-tenant (MSSP)" })
          ] })
        ] })
      ] }),
      mode === "single" && /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Default Tenant" }),
        /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Tenant Name" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                value: tenantName,
                onChange: (e) => setTenantName(e.target.value),
                placeholder: "Acme Corp",
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Tenant Slug" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                value: tenantSlug,
                onChange: (e) => setTenantSlug(e.target.value),
                placeholder: "acme",
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] })
        ] })
      ] }),
      msg && /* @__PURE__ */ jsx("div", { className: "rounded-md bg-green-100 p-4 text-green-700", children: msg }),
      /* @__PURE__ */ jsx("div", { className: "flex justify-end", children: /* @__PURE__ */ jsx(Button, { onClick: handleSave, disabled: saving, children: saving ? "Saving..." : "Finish" }) })
    ] })
  ] }) });
}
export {
  Onboarding as default
};
