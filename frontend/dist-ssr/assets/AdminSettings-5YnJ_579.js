import { jsx, jsxs } from "react/jsx-runtime";
import { useState, useEffect, useMemo, useCallback } from "react";
import { B as Button } from "./Button-C2WBf5y3.js";
function Tabs({ tabs, activeTab, setActiveTab }) {
  return /* @__PURE__ */ jsx("div", { className: "border-b border-border-color", children: /* @__PURE__ */ jsx("nav", { className: "-mb-px flex flex-wrap gap-4 sm:flex-nowrap sm:space-x-8", "aria-label": "Tabs", children: tabs.map((tab) => {
    const isActive = tab.name === activeTab;
    const base = "whitespace-nowrap border-b-2 py-3 px-1 text-sm font-medium transition-colors duration-200";
    const cls = isActive ? "border-primary text-primary" : "border-transparent text-secondary-text hover:border-border-color hover:text-primary-text";
    return /* @__PURE__ */ jsx(
      "button",
      {
        onClick: () => setActiveTab(tab.name),
        className: `${base} ${cls}`,
        type: "button",
        "aria-selected": isActive,
        "aria-controls": `admin-settings-tab-${tab.name}`,
        children: tab.label
      },
      tab.name
    );
  }) }) });
}
function CollapsibleSection({ id, title, helper, defaultOpen = true, children, action }) {
  const [open, setOpen] = useState(defaultOpen);
  const sectionId = id || `collapsible-${title?.toLowerCase().replace(/\s+/g, "-")}`;
  return /* @__PURE__ */ jsxs("section", { className: "rounded-xl border border-border-color bg-gray-50 p-4", children: [
    /* @__PURE__ */ jsxs("header", { className: "flex items-start justify-between gap-3", children: [
      /* @__PURE__ */ jsxs(
        "button",
        {
          type: "button",
          className: "flex flex-1 items-center justify-between text-left",
          onClick: () => setOpen((prev) => !prev),
          "aria-expanded": open,
          "aria-controls": `${sectionId}-content`,
          children: [
            /* @__PURE__ */ jsxs("div", { children: [
              /* @__PURE__ */ jsx("h3", { className: "text-base font-semibold text-primary-text", children: title }),
              helper && /* @__PURE__ */ jsx("p", { className: "mt-1 text-sm text-secondary-text", children: helper })
            ] }),
            /* @__PURE__ */ jsx(
              "svg",
              {
                className: `h-5 w-5 text-secondary-text transition-transform ${open ? "rotate-180" : ""}`,
                viewBox: "0 0 20 20",
                fill: "none",
                xmlns: "http://www.w3.org/2000/svg",
                "aria-hidden": "true",
                children: /* @__PURE__ */ jsx("path", { d: "M6 8l4 4 4-4", stroke: "currentColor", strokeWidth: "1.5", strokeLinecap: "round", strokeLinejoin: "round" })
              }
            )
          ]
        }
      ),
      action ? /* @__PURE__ */ jsx("div", { className: "hidden sm:block", children: action }) : null
    ] }),
    action ? /* @__PURE__ */ jsx("div", { className: "mt-3 sm:hidden", children: action }) : null,
    /* @__PURE__ */ jsx("div", { id: `${sectionId}-content`, className: `mt-4 space-y-4 text-sm ${open ? "block" : "hidden"}`, "aria-hidden": !open, children: open ? children : null })
  ] });
}
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
function BrandingTab({ form, updateField, onValidationChange }) {
  const [errors, setErrors] = useState({});
  const grafanaUrl = form["grafana.url"] || "";
  const emailEnabled = !!form["email.redirect.enabled"];
  const redirectEmail = form["email.redirect.to"] || "";
  useEffect(() => {
    const nextErrors = {};
    if (grafanaUrl && !/^https?:\/\//i.test(grafanaUrl)) {
      nextErrors["grafana.url"] = "Use the root https:// URL; Tenantra proxies /grafana automatically.";
    }
    if (emailEnabled) {
      if (!redirectEmail) {
        nextErrors["email.redirect.to"] = "Provide the inbox address that should receive redirected messages.";
      } else if (!emailRegex.test(redirectEmail)) {
        nextErrors["email.redirect.to"] = "Enter a valid email address (e.g., security@example.com).";
      }
    }
    setErrors(nextErrors);
  }, [grafanaUrl, emailEnabled, redirectEmail]);
  useEffect(() => {
    onValidationChange?.(errors);
  }, [errors, onValidationChange]);
  const httpsSuggestion = useMemo(() => {
    if (!grafanaUrl) return "";
    if (grafanaUrl.startsWith("http://grafana:3000")) {
      return "Detected docker service URL. Consider switching to your HTTPS proxy for production.";
    }
    if (grafanaUrl.startsWith("http://")) {
      return "Grafana is using HTTP. Enable TLS or front it via the Tenantra proxy for secure access.";
    }
    return "";
  }, [grafanaUrl]);
  return /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsx(
      CollapsibleSection,
      {
        id: "branding-theme",
        title: "Brand identity",
        helper: "Set the primary color used across the shell, dashboards, and key call-to-actions.",
        children: /* @__PURE__ */ jsxs("div", { className: "grid gap-4 sm:grid-cols-[max-content_1fr] sm:items-center", children: [
          /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "branding-color", children: "Primary color" }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Impacts the sidebar, primary buttons, and chart accents." }),
            /* @__PURE__ */ jsx(
              "input",
              {
                id: "branding-color",
                type: "color",
                value: form["theme.colors.primary"] || "#1877F2",
                onChange: (e) => updateField("theme.colors.primary", e.target.value),
                className: "mt-2 h-12 w-24 rounded-lg border border-border-color bg-surface"
              }
            )
          ] })
        ] })
      }
    ),
    /* @__PURE__ */ jsx(
      CollapsibleSection,
      {
        id: "branding-grafana",
        title: "Grafana integration",
        helper: "Connect Tenantra to Grafana so metrics widgets load instantly.",
        action: /* @__PURE__ */ jsx(
          "a",
          {
            href: "/app/observability-setup",
            className: "text-sm font-medium text-primary hover:underline",
            children: "Learn more"
          }
        ),
        children: /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "grafana-url", children: "Grafana URL" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Use the root URL; Tenantra automatically proxies /grafana." }),
            /* @__PURE__ */ jsx(
              "input",
              {
                id: "grafana-url",
                type: "url",
                value: grafanaUrl,
                onChange: (e) => updateField("grafana.url", e.target.value.trim()),
                placeholder: "https://grafana.example.com",
                className: `mt-2 block w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${errors["grafana.url"] ? "border-red-500 ring-red-200" : "border-border-color"}`
              }
            ),
            errors["grafana.url"] ? /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-red-500", children: errors["grafana.url"] }) : /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-secondary-text", children: "Example: https://observability.tenantra.com" }),
            httpsSuggestion && /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-amber-600", children: httpsSuggestion })
          ] }),
          /* @__PURE__ */ jsxs("div", { className: "grid gap-4 md:grid-cols-2", children: [
            /* @__PURE__ */ jsxs("div", { children: [
              /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "grafana-dashboard", children: "Dashboard UID" }),
              /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Default Tenantra overview is tenantra-overview." }),
              /* @__PURE__ */ jsx(
                "input",
                {
                  id: "grafana-dashboard",
                  type: "text",
                  value: form["grafana.dashboard_uid"] || "",
                  onChange: (e) => updateField("grafana.dashboard_uid", e.target.value.trim()),
                  placeholder: "tenantra-overview",
                  className: "mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
                }
              )
            ] }),
            /* @__PURE__ */ jsxs("div", { children: [
              /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "grafana-datasource", children: "Datasource UID" }),
              /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Optional. Required if Grafana panels depend on non-default sources." }),
              /* @__PURE__ */ jsx(
                "input",
                {
                  id: "grafana-datasource",
                  type: "text",
                  value: form["grafana.datasource_uid"] || "",
                  onChange: (e) => updateField("grafana.datasource_uid", e.target.value.trim()),
                  placeholder: "prometheus",
                  className: "mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
                }
              )
            ] })
          ] })
        ] })
      }
    ),
    /* @__PURE__ */ jsx(
      CollapsibleSection,
      {
        id: "branding-email",
        title: "Email routing",
        helper: "Redirect system email traffic during staging or incident triage.",
        children: /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxs("label", { className: "flex items-center gap-3 text-sm text-primary-text", htmlFor: "email-redirect-enabled", children: [
            /* @__PURE__ */ jsx(
              "input",
              {
                id: "email-redirect-enabled",
                type: "checkbox",
                checked: emailEnabled,
                onChange: (e) => updateField("email.redirect.enabled", e.target.checked),
                className: "h-4 w-4 rounded border-border-color text-primary focus:ring-primary"
              }
            ),
            "Enable redirect"
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "email-redirect-to", children: "Redirect to" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "All outbound emails will be BCC’d to this address." }),
            /* @__PURE__ */ jsx(
              "input",
              {
                id: "email-redirect-to",
                type: "email",
                disabled: !emailEnabled,
                value: redirectEmail,
                onChange: (e) => updateField("email.redirect.to", e.target.value.trim()),
                placeholder: "security@example.com",
                className: `mt-2 block w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${errors["email.redirect.to"] ? "border-red-500 ring-red-200" : "border-border-color"} ${!emailEnabled ? "bg-gray-100 text-secondary-text" : ""}`
              }
            ),
            emailEnabled && errors["email.redirect.to"] && /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-red-500", children: errors["email.redirect.to"] }),
            emailEnabled && !errors["email.redirect.to"] && /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-secondary-text", children: "Use a shared inbox so the team can monitor rerouted notifications." })
          ] })
        ] })
      }
    )
  ] });
}
function ModulesTab({ headers }) {
  const [list, setList] = useState([]);
  const [saving, setSaving] = useState(false);
  const [groupBy, setGroupBy] = useState("category");
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("/api/admin/modules", { headers });
        if (r.ok) {
          setList(await r.json());
        }
      } catch {
      }
    })();
  }, [headers]);
  const toggle = (id) => {
    setList(
      (prev) => prev.map((m) => m.id === id ? { ...m, enabled: !m.enabled } : m)
    );
  };
  const save = async () => {
    setSaving(true);
    try {
      const enable = list.filter((m) => m.enabled).map((m) => m.id);
      const disable = list.filter((m) => !m.enabled).map((m) => m.id);
      await fetch("/api/admin/modules/bulk", {
        method: "PUT",
        headers,
        body: JSON.stringify({ enable, disable })
      });
    } finally {
      setSaving(false);
    }
  };
  const grouped = (() => {
    if (groupBy === "none") return { All: list };
    const map = {};
    for (const m of list) {
      const key = groupBy === "category" ? m.category || "Uncategorized" : `Phase ${m.phase ?? "-"}`;
      (map[key] || (map[key] = [])).push(m);
    }
    return map;
  })();
  return /* @__PURE__ */ jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-semibold text-primary-text", children: "Modules & Plans" }),
      /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
        /* @__PURE__ */ jsxs(
          "select",
          {
            value: groupBy,
            onChange: (e) => setGroupBy(e.target.value),
            className: "rounded-md border border-border-color px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40",
            children: [
              /* @__PURE__ */ jsx("option", { value: "category", children: "Category" }),
              /* @__PURE__ */ jsx("option", { value: "phase", children: "Phase" }),
              /* @__PURE__ */ jsx("option", { value: "none", children: "None" })
            ]
          }
        ),
        /* @__PURE__ */ jsx(Button, { onClick: save, disabled: saving, children: saving ? "Saving..." : "Save" })
      ] })
    ] }),
    /* @__PURE__ */ jsx("div", { className: "space-y-6", children: Object.entries(grouped).map(([label, items]) => /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("h4", { className: "mb-4 text-base font-medium text-primary-text", children: label }),
      /* @__PURE__ */ jsx("div", { className: "grid grid-cols-1 gap-6 md:grid-cols-2", children: items.map((m) => /* @__PURE__ */ jsxs(
        "label",
        {
          className: "flex items-center rounded-lg border border-border-color bg-surface p-4 shadow-sm",
          children: [
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "checkbox",
                checked: !!m.enabled,
                onChange: () => toggle(m.id),
                className: "h-4 w-4 rounded border-border-color text-primary focus:ring-primary"
              }
            ),
            /* @__PURE__ */ jsxs("div", { className: "ml-4", children: [
              /* @__PURE__ */ jsx("div", { className: "text-sm font-medium text-primary-text", children: m.name }),
              /* @__PURE__ */ jsxs("div", { className: "text-xs text-secondary-text", children: [
                "Phase ",
                m.phase ?? "-",
                " · ",
                m.category ?? "-"
              ] })
            ] })
          ]
        },
        m.id
      )) })
    ] }, label)) })
  ] });
}
function LogsTab({ headers }) {
  const [lines, setLines] = useState([]);
  const [path, setPath] = useState("");
  const [error, setError] = useState("");
  const [auto, setAuto] = useState(true);
  const [intervalMs, setIntervalMs] = useState(3e3);
  const refresh = useCallback(async () => {
    setError("");
    try {
      const r = await fetch("/api/admin/app/logs", { headers });
      if (r.ok) {
        const j = await r.json();
        setLines(j.lines || []);
        setPath(j.path || "");
      } else {
        const j = await r.json().catch(() => ({ detail: `HTTP ${r.status}` }));
        setError(j.detail || `HTTP ${r.status}`);
      }
    } catch (e) {
      setError(String(e));
    }
  }, [headers]);
  useEffect(() => {
    refresh();
  }, [refresh]);
  useEffect(() => {
    if (!auto) return;
    const id = setInterval(refresh, Math.max(1e3, intervalMs));
    return () => clearInterval(id);
  }, [auto, intervalMs, refresh]);
  return /* @__PURE__ */ jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxs("h3", { className: "text-lg font-semibold text-primary-text", children: [
        "App Logs (tail)",
        path ? ` — ${path}` : ""
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
        /* @__PURE__ */ jsxs("label", { className: "flex items-center text-sm", children: [
          /* @__PURE__ */ jsx(
            "input",
            {
              type: "checkbox",
              checked: auto,
              onChange: (e) => setAuto(e.target.checked),
              className: "h-4 w-4 rounded border-border-color text-primary focus:ring-primary"
            }
          ),
          /* @__PURE__ */ jsx("span", { className: "ml-2", children: "Auto-refresh" })
        ] }),
        /* @__PURE__ */ jsx(
          "input",
          {
            type: "number",
            min: "1000",
            step: "500",
            value: intervalMs,
            onChange: (e) => setIntervalMs(Number(e.target.value) || 3e3),
            className: "w-24 rounded-md border border-border-color px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
          }
        ),
        /* @__PURE__ */ jsx(Button, { onClick: refresh, children: "Refresh" })
      ] })
    ] }),
    error && /* @__PURE__ */ jsxs("div", { className: "rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700", children: [
      error,
      " ",
      error.includes("not found") && "(check LOG_FILE_PATH and backend log path)"
    ] }),
    /* @__PURE__ */ jsx("pre", { className: "max-h-96 overflow-auto rounded-lg bg-gray-900 p-4 text-sm text-green-400", children: /* @__PURE__ */ jsx("code", { children: lines.join("\n") }) })
  ] });
}
const CACHE_KEY = "tena_observability_health";
const formatRelative = (iso) => {
  if (!iso) return "";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "";
  const diffMs = Date.now() - then;
  const diffMinutes = Math.round(diffMs / 6e4);
  if (diffMinutes <= 0) return "just now";
  if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes === 1 ? "" : "s"} ago`;
  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? "" : "s"} ago`;
  const diffDays = Math.round(diffHours / 24);
  return `${diffDays} day${diffDays === 1 ? "" : "s"} ago`;
};
const readCachedHealth = () => {
  try {
    if (typeof window === "undefined") return null;
    const raw = window.localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || !parsed.meta) return null;
    return parsed;
  } catch {
    return null;
  }
};
const writeCachedHealth = (payload) => {
  try {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(CACHE_KEY, JSON.stringify(payload));
  } catch {
  }
};
function ObservabilityTab({ headers, onSavedHealth }) {
  const [statusPayload, setStatusPayload] = useState(null);
  const [healthMeta, setHealthMeta] = useState(null);
  const [activeProbe, setActiveProbe] = useState("Grafana health");
  const [uid, setUid] = useState("tenantra-overview");
  const [dsUid, setDsUid] = useState("");
  const [slug, setSlug] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [isChecking, setIsChecking] = useState(false);
  const grafanaUrl = useMemo(() => {
    if (typeof window === "undefined") return "";
    try {
      const stored = window.localStorage.getItem("grafana:url:hint");
      if (stored) return stored;
    } catch {
    }
    return "";
  }, []);
  const setFieldError = useCallback((key, message) => {
    setFieldErrors((prev) => {
      if (message) return { ...prev, [key]: message };
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }, []);
  const runCheck = useCallback(
    async ({ url, label, cacheResult = false }) => {
      setIsChecking(true);
      setActiveProbe(label);
      setStatusPayload(null);
      const started = performance.now();
      let toastMessage = "";
      try {
        const response = await fetch(url, { headers });
        const body = await response.json();
        const durationMs = Math.round(performance.now() - started);
        setStatusPayload(body);
        const meta = {
          label,
          at: (/* @__PURE__ */ new Date()).toISOString(),
          status: response.status,
          durationMs,
          payload: body
        };
        if (!response.ok) {
          const errorDetail = body?.detail || `HTTP ${response.status}`;
          toastMessage = `${label} failed • ${errorDetail}`;
          try {
            window.dispatchEvent(
              new CustomEvent("tena:notice", {
                detail: { kind: "error", message: toastMessage }
              })
            );
          } catch {
          }
          return;
        }
        toastMessage = `${label} succeeded • ${durationMs} ms`;
        try {
          window.dispatchEvent(
            new CustomEvent("tena:notice", {
              detail: { kind: "success", message: toastMessage }
            })
          );
        } catch {
        }
        if (cacheResult) {
          const payload = { meta, body };
          setHealthMeta(meta);
          writeCachedHealth(payload);
          try {
            window.localStorage.setItem("grafana:url:hint", body?.grafana_url || "");
          } catch {
          }
          onSavedHealth?.(meta);
        }
      } catch (error) {
        const errorText = error instanceof Error ? error.message : "Unable to complete request";
        setStatusPayload({ error: errorText });
        toastMessage = `${label} failed • ${errorText}`;
        try {
          window.dispatchEvent(
            new CustomEvent("tena:notice", {
              detail: { kind: "error", message: toastMessage }
            })
          );
        } catch {
        }
      } finally {
        setIsChecking(false);
      }
    },
    [headers, onSavedHealth]
  );
  useEffect(() => {
    const cached = readCachedHealth();
    if (!cached) return;
    setStatusPayload(cached.body);
    setHealthMeta(cached.meta);
    setActiveProbe(cached.meta.label || "Grafana health");
  }, []);
  const handleHealthCheck = () => {
    runCheck({ url: "/api/admin/observability/grafana/health", label: "Grafana health check", cacheResult: true });
  };
  const handleUidCheck = () => {
    if (!uid.trim()) {
      setFieldError("uid", "Enter the dashboard UID you want to probe.");
      return;
    }
    setFieldError("uid", "");
    runCheck({
      url: `/api/admin/observability/grafana/dashboard/${encodeURIComponent(uid.trim())}`,
      label: `Dashboard UID ${uid.trim()}`
    });
  };
  const handleDatasourceCheck = () => {
    if (!dsUid.trim()) {
      setFieldError("dsUid", "Provide the datasource UID (found under Grafana → Connections).");
      return;
    }
    setFieldError("dsUid", "");
    runCheck({
      url: `/api/admin/observability/grafana/datasource/${encodeURIComponent(dsUid.trim())}`,
      label: `Datasource UID ${dsUid.trim()}`
    });
  };
  const handleSlugCheck = () => {
    if (!slug.trim()) {
      setFieldError("slug", "Paste the dashboard slug (URL fragment) you want to validate.");
      return;
    }
    setFieldError("slug", "");
    runCheck({
      url: `/api/admin/observability/grafana/dashboard/slug/${encodeURIComponent(slug.trim())}`,
      label: `Dashboard slug ${slug.trim()}`
    });
  };
  const lastCheckDescription = useMemo(() => {
    if (!healthMeta) return "No successful check yet.";
    const relative = formatRelative(healthMeta.at);
    const latency = typeof healthMeta.durationMs === "number" ? `${healthMeta.durationMs} ms` : "";
    return `Last check: ${relative} • HTTP ${healthMeta.status}${latency ? ` • ${latency}` : ""}`;
  }, [healthMeta]);
  return /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsx(
      CollapsibleSection,
      {
        id: "observability-health",
        title: "Grafana connectivity",
        helper: "Run the health probe before enabling dashboards in production.",
        action: /* @__PURE__ */ jsx(
          "a",
          {
            href: grafanaUrl || "/grafana",
            target: "_blank",
            rel: "noopener noreferrer",
            className: "text-sm font-medium text-primary hover:underline",
            children: "Open Grafana"
          }
        ),
        children: /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsx("div", { className: "rounded-lg border border-border-color bg-surface px-4 py-3 text-sm text-secondary-text", children: lastCheckDescription }),
          /* @__PURE__ */ jsx(
            Button,
            {
              onClick: handleHealthCheck,
              disabled: isChecking,
              className: "w-full",
              size: "lg",
              children: isChecking && activeProbe === "Grafana health check" ? "Checking..." : "Run health check"
            }
          )
        ] })
      }
    ),
    /* @__PURE__ */ jsx(
      CollapsibleSection,
      {
        id: "observability-diagnostics",
        title: "Dashboard diagnostics",
        helper: "Validate your Grafana identifiers before wiring widgets.",
        children: /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "diagnostic-uid", children: "Dashboard UID" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Capture it from Grafana → Dashboards → Settings." }),
            /* @__PURE__ */ jsxs("div", { className: "mt-2 flex flex-col gap-3 md:flex-row", children: [
              /* @__PURE__ */ jsx(
                "input",
                {
                  id: "diagnostic-uid",
                  value: uid,
                  onChange: (e) => setUid(e.target.value),
                  className: `w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${fieldErrors.uid ? "border-red-500 ring-red-200" : "border-border-color"}`,
                  placeholder: "tenantra-overview"
                }
              ),
              /* @__PURE__ */ jsx(
                Button,
                {
                  variant: "ghost",
                  onClick: handleUidCheck,
                  disabled: isChecking,
                  className: "w-full md:w-auto",
                  children: isChecking && activeProbe.startsWith("Dashboard UID") ? "Checking..." : "Check UID"
                }
              )
            ] }),
            fieldErrors.uid && /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-red-500", children: fieldErrors.uid })
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "diagnostic-datasource", children: "Datasource UID" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Optional, but useful when running custom Prometheus/Uptime panels." }),
            /* @__PURE__ */ jsxs("div", { className: "mt-2 flex flex-col gap-3 md:flex-row", children: [
              /* @__PURE__ */ jsx(
                "input",
                {
                  id: "diagnostic-datasource",
                  value: dsUid,
                  onChange: (e) => setDsUid(e.target.value),
                  className: `w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${fieldErrors.dsUid ? "border-red-500 ring-red-200" : "border-border-color"}`,
                  placeholder: "prometheus"
                }
              ),
              /* @__PURE__ */ jsx(
                Button,
                {
                  variant: "ghost",
                  onClick: handleDatasourceCheck,
                  disabled: isChecking,
                  className: "w-full md:w-auto",
                  children: isChecking && activeProbe.startsWith("Datasource") ? "Checking..." : "Check datasource"
                }
              )
            ] }),
            fieldErrors.dsUid && /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-red-500", children: fieldErrors.dsUid })
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "diagnostic-slug", children: "Dashboard slug" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Slug matches the URL path (e.g., observability-overview)." }),
            /* @__PURE__ */ jsxs("div", { className: "mt-2 flex flex-col gap-3 md:flex-row", children: [
              /* @__PURE__ */ jsx(
                "input",
                {
                  id: "diagnostic-slug",
                  value: slug,
                  onChange: (e) => setSlug(e.target.value),
                  className: `w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${fieldErrors.slug ? "border-red-500 ring-red-200" : "border-border-color"}`,
                  placeholder: "tenantra-overview"
                }
              ),
              /* @__PURE__ */ jsx(
                Button,
                {
                  variant: "ghost",
                  onClick: handleSlugCheck,
                  disabled: isChecking,
                  className: "w-full md:w-auto",
                  children: isChecking && activeProbe.startsWith("Dashboard slug") ? "Checking..." : "Check slug"
                }
              )
            ] }),
            fieldErrors.slug && /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-red-500", children: fieldErrors.slug })
          ] })
        ] })
      }
    ),
    /* @__PURE__ */ jsxs(
      CollapsibleSection,
      {
        id: "observability-diagnostics-json",
        title: "Diagnostics payload",
        helper: "Raw JSON is available for deep dives and support tickets.",
        defaultOpen: false,
        children: [
          statusPayload ? /* @__PURE__ */ jsx("pre", { className: "max-h-80 overflow-auto rounded-lg bg-gray-900 p-4 text-xs text-gray-100", children: /* @__PURE__ */ jsx("code", { children: JSON.stringify(statusPayload, null, 2) }) }) : /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Run a probe to populate diagnostics." }),
          statusPayload?.detail === "grafana.url not configured" && /* @__PURE__ */ jsx("p", { className: "mt-4 text-xs text-amber-600", children: "grafana.url is missing. Navigate to Branding → Grafana integration to configure it, then re-run the health check." })
        ]
      }
    )
  ] });
}
function AuditsTab({ headers }) {
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [total, pageSize]);
  const refresh = useCallback(async () => {
    const params = new URLSearchParams();
    if (dateFrom) params.set("start_date", dateFrom);
    if (dateTo) params.set("end_date", dateTo);
    if (result) params.set("result", result);
    params.set("page", String(page));
    params.set("page_size", String(pageSize));
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`/api/audit-logs?${params.toString()}`, { headers });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        if (response.status >= 500) {
          setError("Audit service unavailable; check backend logs or run make validate.");
        } else {
          setError(detail.detail || `Unable to fetch audit logs (HTTP ${response.status}).`);
        }
        setItems([]);
        setTotal(0);
        return;
      }
      const payload = await response.json();
      setItems(payload.items || []);
      setTotal(payload.total || 0);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Network error";
      setError(`Unable to reach audit API • ${message}`);
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [headers, dateFrom, dateTo, result, page, pageSize]);
  useEffect(() => {
    refresh();
  }, [refresh]);
  const filtered = useMemo(
    () => items.filter((it) => !q || JSON.stringify(it).toLowerCase().includes(q.toLowerCase())),
    [items, q]
  );
  return /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
    /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between", children: [
      /* @__PURE__ */ jsx("h3", { className: "text-lg font-semibold text-primary-text", children: "Audit logs" }),
      /* @__PURE__ */ jsx(Button, { onClick: refresh, disabled: loading, className: "w-full sm:w-auto", children: loading ? "Refreshing..." : "Apply filters" })
    ] }),
    /* @__PURE__ */ jsx(
      CollapsibleSection,
      {
        id: "audit-filters",
        title: "Filters",
        helper: "Narrow results by window, result, or keyword before exporting.",
        children: /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-4 md:grid-cols-4", children: [
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "audit-search", children: "Search" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Matches event payload, actor, and metadata." }),
            /* @__PURE__ */ jsx(
              "input",
              {
                id: "audit-search",
                value: q,
                onChange: (e) => setQ(e.target.value),
                className: "mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40",
                placeholder: "Find events..."
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "audit-start", children: "Start date" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "UTC date; leave blank for oldest data." }),
            /* @__PURE__ */ jsx(
              "input",
              {
                id: "audit-start",
                type: "date",
                value: dateFrom,
                onChange: (e) => setDateFrom(e.target.value),
                className: "mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "audit-end", children: "End date" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Inclusive. Combine with start date for bounded range." }),
            /* @__PURE__ */ jsx(
              "input",
              {
                id: "audit-end",
                type: "date",
                value: dateTo,
                onChange: (e) => setDateTo(e.target.value),
                className: "mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-primary-text", htmlFor: "audit-result", children: "Result" }),
            /* @__PURE__ */ jsx("p", { className: "text-xs text-secondary-text", children: "Surface failures quickly when triaging incidents." }),
            /* @__PURE__ */ jsxs(
              "select",
              {
                id: "audit-result",
                value: result,
                onChange: (e) => setResult(e.target.value),
                className: "mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40",
                children: [
                  /* @__PURE__ */ jsx("option", { value: "", children: "Any" }),
                  /* @__PURE__ */ jsx("option", { value: "success", children: "Success" }),
                  /* @__PURE__ */ jsx("option", { value: "failure", children: "Failure" }),
                  /* @__PURE__ */ jsx("option", { value: "denied", children: "Denied" })
                ]
              }
            )
          ] })
        ] })
      }
    ),
    error && /* @__PURE__ */ jsx("div", { className: "rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-700", children: error }),
    !error && /* @__PURE__ */ jsx("div", { className: "overflow-hidden rounded-lg border border-border-color shadow", children: /* @__PURE__ */ jsxs("table", { className: "min-w-full divide-y divide-border-color", children: [
      /* @__PURE__ */ jsx("thead", { className: "bg-gray-50", children: /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-secondary-text", children: "Time" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-secondary-text", children: "User" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-secondary-text", children: "Action" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-secondary-text", children: "Result" })
      ] }) }),
      /* @__PURE__ */ jsx("tbody", { className: "divide-y divide-border-color bg-surface", children: filtered.length === 0 ? /* @__PURE__ */ jsx("tr", { children: /* @__PURE__ */ jsx("td", { colSpan: 4, className: "px-6 py-6 text-center text-sm text-secondary-text", children: loading ? "Loading audit activity…" : "No audit entries match your filters yet." }) }) : filtered.map((row, index) => /* @__PURE__ */ jsxs("tr", { className: "hover:bg-gray-50/60", children: [
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-3 text-sm text-primary-text", children: row.timestamp || row.created_at || "" }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-3 text-sm text-primary-text", children: row.user_id || "—" }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-3 text-sm text-primary-text", children: row.action || "" }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-3 text-sm text-primary-text capitalize", children: row.result || "" })
      ] }, index)) })
    ] }) }),
    /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between", children: [
      /* @__PURE__ */ jsxs("div", { className: "text-sm text-secondary-text", children: [
        "Total events: ",
        total
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-2 sm:flex-row sm:items-center", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between gap-2", children: [
          /* @__PURE__ */ jsx(Button, { onClick: () => setPage((p) => Math.max(1, p - 1)), disabled: page <= 1 || loading, variant: "ghost", children: "Prev" }),
          /* @__PURE__ */ jsxs("div", { className: "text-sm text-primary-text", children: [
            "Page ",
            page,
            " / ",
            totalPages
          ] }),
          /* @__PURE__ */ jsx(
            Button,
            {
              onClick: () => setPage((p) => Math.min(totalPages, p + 1)),
              disabled: page >= totalPages || loading,
              variant: "ghost",
              children: "Next"
            }
          )
        ] }),
        /* @__PURE__ */ jsx(
          "select",
          {
            value: pageSize,
            onChange: (e) => {
              setPageSize(Number(e.target.value) || 50);
              setPage(1);
            },
            className: "rounded-lg border border-border-color px-3 py-2 text-sm text-primary-text focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40",
            children: [25, 50, 100, 200, 500].map((n) => /* @__PURE__ */ jsxs("option", { value: n, children: [
              n,
              " / page"
            ] }, n))
          }
        )
      ] })
    ] })
  ] });
}
const TABS = [
  { name: "branding", label: "Branding" },
  { name: "modules", label: "Modules" },
  { name: "logs", label: "Logs" },
  { name: "observability", label: "Observability" },
  { name: "audits", label: "Audits" }
];
function AdminSettings() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [tab, setTab] = useState("branding");
  const [lastSavedAt, setLastSavedAt] = useState("");
  const [saveStatus, setSaveStatus] = useState({ kind: "", message: "" });
  const [brandingErrors, setBrandingErrors] = useState({});
  const [lastHealthMeta, setLastHealthMeta] = useState(null);
  const [form, setForm] = useState({
    "theme.colors.primary": "#1877F2",
    "email.redirect.enabled": false,
    "email.redirect.to": "",
    "grafana.url": "",
    "grafana.dashboard_uid": "tenantra-overview",
    "grafana.datasource_uid": "prometheus",
    "worker.enabled": true
  });
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const tid = typeof window !== "undefined" ? localStorage.getItem("tenant_id") : null;
  const headers = useMemo(() => {
    const base = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
    return tid ? { ...base, "X-Tenant-Id": tid } : base;
  }, [token, tid]);
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/admin/settings", { headers });
        if (res.ok) {
          const items = await res.json();
          setForm((prev) => {
            const next = { ...prev };
            for (const it of items) next[it.key] = it.value;
            return next;
          });
        }
      } catch {
      }
      setLoading(false);
    })();
  }, [headers]);
  const updateField = useCallback((key, val) => {
    setForm((prev) => ({ ...prev, [key]: val }));
  }, []);
  useEffect(() => {
    try {
      if (typeof window === "undefined") return;
      const raw = window.localStorage.getItem("tena_observability_health");
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed?.meta) {
        setLastHealthMeta(parsed.meta);
      }
    } catch {
    }
  }, []);
  const formatRelativeTime = useCallback((iso) => {
    if (!iso) return "";
    const then = new Date(iso).getTime();
    if (Number.isNaN(then)) return "";
    const diffMs = Date.now() - then;
    if (diffMs < 6e4) return "just now";
    const diffMinutes = Math.round(diffMs / 6e4);
    if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes === 1 ? "" : "s"} ago`;
    const diffHours = Math.round(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? "" : "s"} ago`;
    const diffDays = Math.round(diffHours / 24);
    return `${diffDays} day${diffDays === 1 ? "" : "s"} ago`;
  }, []);
  const hasBlockingErrors = useMemo(
    () => brandingErrors && Object.keys(brandingErrors).length > 0,
    [brandingErrors]
  );
  const handleSave = async () => {
    if (hasBlockingErrors) {
      const message = "Resolve the highlighted validation errors before saving.";
      setSaveStatus({ kind: "error", message });
      try {
        window.dispatchEvent(
          new CustomEvent("tena:notice", {
            detail: { kind: "error", message }
          })
        );
      } catch {
      }
      return;
    }
    setSaving(true);
    setSaveStatus({ kind: "", message: "" });
    try {
      const res = await fetch("/api/admin/settings", { method: "PUT", headers, body: JSON.stringify(form) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const savedAt = (/* @__PURE__ */ new Date()).toISOString();
      setLastSavedAt(savedAt);
      const formatted = new Date(savedAt).toLocaleString();
      setSaveStatus({ kind: "success", message: `Settings saved • ${formatted}` });
      try {
        window.dispatchEvent(
          new CustomEvent("tena:notice", {
            detail: { kind: "success", message: `Settings saved • ${formatted}` }
          })
        );
      } catch {
      }
      if (form["theme.colors.primary"]) {
        document.documentElement.style.setProperty("--tena-primary", form["theme.colors.primary"]);
        try {
          window.dispatchEvent(new CustomEvent("tena:settings-updated", { detail: { key: "theme.colors.primary", value: form["theme.colors.primary"] } }));
        } catch {
        }
      }
      try {
        if (typeof window !== "undefined") {
          window.localStorage.setItem("grafana:url:hint", form["grafana.url"] || "");
        }
      } catch {
      }
    } catch (e) {
      const reason = e instanceof Error ? e.message : "Save failed";
      setSaveStatus({ kind: "error", message: reason });
      try {
        window.dispatchEvent(
          new CustomEvent("tena:notice", {
            detail: { kind: "error", message: reason || "Unable to save settings" }
          })
        );
      } catch {
      }
    } finally {
      setSaving(false);
    }
  };
  const primaryColor = form["theme.colors.primary"] || "#1877F2";
  const grafanaUrl = form["grafana.url"] || "Not configured";
  const workersEnabled = Boolean(form["worker.enabled"]);
  const lastHealthSummary = lastHealthMeta ? `HTTP ${lastHealthMeta.status} • ${lastHealthMeta.durationMs ?? "—"} ms • ${formatRelativeTime(lastHealthMeta.at)}` : "No successful check yet";
  if (loading) return /* @__PURE__ */ jsx("div", { className: "p-10 text-center text-primary-text", children: "Loading..." });
  return /* @__PURE__ */ jsx("div", { className: "min-h-screen bg-surface px-4 py-8 sm:px-6 lg:px-8", children: /* @__PURE__ */ jsxs("div", { className: "mx-auto max-w-6xl space-y-6", children: [
    /* @__PURE__ */ jsxs("header", { className: "space-y-2", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-semibold text-primary-text", children: "Admin Settings" }),
      /* @__PURE__ */ jsx("p", { className: "text-sm text-secondary-text", children: "Configure branding, observability, and platform controls for your tenants with inline diagnostics and helper guidance." })
    ] }),
    /* @__PURE__ */ jsxs("section", { className: "rounded-xl border border-border-color bg-surface p-6 shadow", children: [
      /* @__PURE__ */ jsx("h2", { className: "text-sm font-semibold uppercase tracking-wide text-secondary-text", children: "Current configuration" }),
      /* @__PURE__ */ jsxs("div", { className: "mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-5", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 rounded-lg bg-gray-100 p-4", children: [
          /* @__PURE__ */ jsx(
            "span",
            {
              className: "h-10 w-10 flex-shrink-0 rounded-full border border-border-color",
              style: { backgroundColor: primaryColor },
              "aria-label": `Primary color swatch ${primaryColor}`
            }
          ),
          /* @__PURE__ */ jsxs("div", { className: "text-sm", children: [
            /* @__PURE__ */ jsx("div", { className: "font-medium text-primary-text", children: "Primary color" }),
            /* @__PURE__ */ jsx("div", { className: "text-secondary-text", children: primaryColor })
          ] })
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "rounded-lg bg-gray-100 p-4 text-sm", children: [
          /* @__PURE__ */ jsx("div", { className: "font-medium text-primary-text", children: "Grafana URL" }),
          /* @__PURE__ */ jsx("div", { className: "text-secondary-text break-all", children: grafanaUrl.startsWith("http") ? grafanaUrl : "Not configured" })
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "rounded-lg bg-gray-100 p-4 text-sm", children: [
          /* @__PURE__ */ jsx("div", { className: "font-medium text-primary-text", children: "Workers" }),
          /* @__PURE__ */ jsx("div", { className: `font-medium ${workersEnabled ? "text-green-600" : "text-red-500"}`, children: workersEnabled ? "Enabled" : "Disabled" })
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "rounded-lg bg-gray-100 p-4 text-sm", children: [
          /* @__PURE__ */ jsx("div", { className: "font-medium text-primary-text", children: "Last saved" }),
          /* @__PURE__ */ jsx("div", { className: "text-secondary-text", children: lastSavedAt ? new Date(lastSavedAt).toLocaleString() : "Not yet saved" })
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "rounded-lg bg-gray-100 p-4 text-sm", children: [
          /* @__PURE__ */ jsx("div", { className: "font-medium text-primary-text", children: "Grafana health" }),
          /* @__PURE__ */ jsx("div", { className: "text-secondary-text", children: lastHealthSummary })
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsx(Tabs, { tabs: TABS, activeTab: tab, setActiveTab: setTab }),
    /* @__PURE__ */ jsxs("div", { className: "rounded-xl border border-border-color bg-surface p-6 shadow", children: [
      tab === "branding" && /* @__PURE__ */ jsx("div", { id: "admin-settings-tab-branding", children: /* @__PURE__ */ jsx(
        BrandingTab,
        {
          form,
          updateField,
          onValidationChange: (errs) => setBrandingErrors(errs || {})
        }
      ) }),
      tab === "modules" && /* @__PURE__ */ jsx("div", { id: "admin-settings-tab-modules", children: /* @__PURE__ */ jsx(ModulesTab, { headers }) }),
      tab === "logs" && /* @__PURE__ */ jsx("div", { id: "admin-settings-tab-logs", children: /* @__PURE__ */ jsx(LogsTab, { headers }) }),
      tab === "observability" && /* @__PURE__ */ jsx("div", { id: "admin-settings-tab-observability", children: /* @__PURE__ */ jsx(
        ObservabilityTab,
        {
          headers,
          onSavedHealth: (meta) => {
            if (!meta) return;
            setLastHealthMeta(meta);
            try {
              window.dispatchEvent(new CustomEvent("tena:settings-observability", { detail: meta }));
            } catch {
            }
          }
        }
      ) }),
      tab === "audits" && /* @__PURE__ */ jsx("div", { id: "admin-settings-tab-audits", children: /* @__PURE__ */ jsx(AuditsTab, { headers }) })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-3 rounded-xl border border-border-color bg-surface p-6 shadow sm:flex-row sm:items-center sm:justify-between", children: [
      /* @__PURE__ */ jsx("div", { className: "text-sm text-secondary-text", children: saveStatus.message ? /* @__PURE__ */ jsx("span", { className: saveStatus.kind === "error" ? "text-red-500" : "text-green-600", children: saveStatus.message }) : "Save applies updates across tenants instantly." }),
      /* @__PURE__ */ jsx(
        Button,
        {
          onClick: handleSave,
          disabled: saving || hasBlockingErrors,
          className: "w-full sm:w-auto",
          size: "lg",
          children: saving ? "Saving..." : "Save settings"
        }
      )
    ] })
  ] }) });
}
export {
  AdminSettings as default
};
