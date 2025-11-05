import React, { useEffect, useState, useCallback, useMemo } from "react";
import Tabs from "../components/admin/Tabs.jsx";
import BrandingTab from "../components/admin/BrandingTab.jsx";
import ModulesTab from "../components/admin/ModulesTab.jsx";
import LogsTab from "../components/admin/LogsTab.jsx";
import ObservabilityTab from "../components/admin/ObservabilityTab.jsx";
import AuditsTab from "../components/admin/AuditsTab.jsx";
import Button from "../components/ui/Button.jsx";

const TABS = [
  { name: "branding", label: "Branding" },
  { name: "modules", label: "Modules" },
  { name: "logs", label: "Logs" },
  { name: "observability", label: "Observability" },
  { name: "audits", label: "Audits" },
];

export default function AdminSettings() {
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
    "worker.enabled": true,
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
      } catch {}
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
    } catch {}
  }, []);

  const formatRelativeTime = useCallback((iso) => {
    if (!iso) return "";
    const then = new Date(iso).getTime();
    if (Number.isNaN(then)) return "";
    const diffMs = Date.now() - then;
    if (diffMs < 60000) return "just now";
    const diffMinutes = Math.round(diffMs / 60000);
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
            detail: { kind: "error", message },
          })
        );
      } catch {}
      return;
    }
    setSaving(true);
    setSaveStatus({ kind: "", message: "" });
    try {
      const res = await fetch("/api/admin/settings", { method: "PUT", headers, body: JSON.stringify(form) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const savedAt = new Date().toISOString();
      setLastSavedAt(savedAt);
      const formatted = new Date(savedAt).toLocaleString();
      setSaveStatus({ kind: "success", message: `Settings saved • ${formatted}` });
      try {
        window.dispatchEvent(
          new CustomEvent("tena:notice", {
            detail: { kind: "success", message: `Settings saved • ${formatted}` },
          })
        );
      } catch {}
      if (form["theme.colors.primary"]) {
        document.documentElement.style.setProperty("--tena-primary", form["theme.colors.primary"]);
        try {
          window.dispatchEvent(new CustomEvent("tena:settings-updated", { detail: { key: "theme.colors.primary", value: form["theme.colors.primary"] } }));
        } catch {}
      }
      try {
        if (typeof window !== "undefined") {
          window.localStorage.setItem("grafana:url:hint", form["grafana.url"] || "");
        }
      } catch {}
    } catch (e) {
      const reason = e instanceof Error ? e.message : "Save failed";
      setSaveStatus({ kind: "error", message: reason });
      try {
        window.dispatchEvent(
          new CustomEvent("tena:notice", {
            detail: { kind: "error", message: reason || "Unable to save settings" },
          })
        );
      } catch {}
    } finally {
      setSaving(false);
    }
  };

  const primaryColor = form["theme.colors.primary"] || "#1877F2";
  const grafanaUrl = form["grafana.url"] || "Not configured";
  const workersEnabled = Boolean(form["worker.enabled"]);
  const lastHealthSummary = lastHealthMeta
    ? `HTTP ${lastHealthMeta.status} • ${lastHealthMeta.durationMs ?? "—"} ms • ${formatRelativeTime(lastHealthMeta.at)}`
    : "No successful check yet";

  if (loading) return <div className="p-10 text-center text-primary-text">Loading...</div>;

  return (
    <div className="min-h-screen bg-surface px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold text-primary-text">Admin Settings</h1>
          <p className="text-sm text-secondary-text">
            Configure branding, observability, and platform controls for your tenants with inline diagnostics and helper guidance.
          </p>
        </header>

        <section className="rounded-xl border border-border-color bg-surface p-6 shadow">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-secondary-text">Current configuration</h2>
          <div className="mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
            <div className="flex items-center gap-3 rounded-lg bg-gray-100 p-4">
              <span
                className="h-10 w-10 flex-shrink-0 rounded-full border border-border-color"
                style={{ backgroundColor: primaryColor }}
                aria-label={`Primary color swatch ${primaryColor}`}
              />
              <div className="text-sm">
                <div className="font-medium text-primary-text">Primary color</div>
                <div className="text-secondary-text">{primaryColor}</div>
              </div>
            </div>
            <div className="rounded-lg bg-gray-100 p-4 text-sm">
              <div className="font-medium text-primary-text">Grafana URL</div>
              <div className="text-secondary-text break-all">
                {grafanaUrl.startsWith("http") ? grafanaUrl : "Not configured"}
              </div>
            </div>
            <div className="rounded-lg bg-gray-100 p-4 text-sm">
              <div className="font-medium text-primary-text">Workers</div>
              <div className={`font-medium ${workersEnabled ? "text-green-600" : "text-red-500"}`}>
                {workersEnabled ? "Enabled" : "Disabled"}
              </div>
            </div>
            <div className="rounded-lg bg-gray-100 p-4 text-sm">
              <div className="font-medium text-primary-text">Last saved</div>
              <div className="text-secondary-text">{lastSavedAt ? new Date(lastSavedAt).toLocaleString() : "Not yet saved"}</div>
            </div>
            <div className="rounded-lg bg-gray-100 p-4 text-sm">
              <div className="font-medium text-primary-text">Grafana health</div>
              <div className="text-secondary-text">{lastHealthSummary}</div>
            </div>
          </div>
        </section>

        <Tabs tabs={TABS} activeTab={tab} setActiveTab={setTab} />

        <div className="rounded-xl border border-border-color bg-surface p-6 shadow">
          {tab === "branding" && (
            <div id="admin-settings-tab-branding">
              <BrandingTab
                form={form}
                updateField={updateField}
                onValidationChange={(errs) => setBrandingErrors(errs || {})}
              />
            </div>
          )}
          {tab === "modules" && (
            <div id="admin-settings-tab-modules">
              <ModulesTab headers={headers} />
            </div>
          )}
          {tab === "logs" && (
            <div id="admin-settings-tab-logs">
              <LogsTab headers={headers} />
            </div>
          )}
          {tab === "observability" && (
            <div id="admin-settings-tab-observability">
              <ObservabilityTab
                headers={headers}
                onSavedHealth={(meta) => {
                  if (!meta) return;
                  setLastHealthMeta(meta);
                  try {
                    window.dispatchEvent(new CustomEvent("tena:settings-observability", { detail: meta }));
                  } catch {}
                }}
              />
            </div>
          )}
          {tab === "audits" && (
            <div id="admin-settings-tab-audits">
              <AuditsTab headers={headers} />
            </div>
          )}
        </div>

        <div className="flex flex-col gap-3 rounded-xl border border-border-color bg-surface p-6 shadow sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-secondary-text">
            {saveStatus.message ? (
              <span className={saveStatus.kind === "error" ? "text-red-500" : "text-green-600"}>{saveStatus.message}</span>
            ) : (
              "Save applies updates across tenants instantly."
            )}
          </div>
          <Button
            onClick={handleSave}
            disabled={saving || hasBlockingErrors}
            className="w-full sm:w-auto"
            size="lg"
          >
            {saving ? "Saving..." : "Save settings"}
          </Button>
        </div>
      </div>
    </div>
  );
}
