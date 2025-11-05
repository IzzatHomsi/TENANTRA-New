import React, { useCallback, useEffect, useMemo, useState, memo } from "react";
import CollapsibleSection from "./CollapsibleSection.jsx";
import Button from "../ui/Button.jsx";

const CACHE_KEY = "tena_observability_health";

const formatRelative = (iso) => {
  if (!iso) return "";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "";
  const diffMs = Date.now() - then;
  const diffMinutes = Math.round(diffMs / 60000);
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
  } catch {}
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
    } catch {}
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
          at: new Date().toISOString(),
          status: response.status,
          durationMs,
          payload: body,
        };
        if (!response.ok) {
          const errorDetail = body?.detail || `HTTP ${response.status}`;
          toastMessage = `${label} failed • ${errorDetail}`;
          try {
            window.dispatchEvent(
              new CustomEvent("tena:notice", {
                detail: { kind: "error", message: toastMessage },
              })
            );
          } catch {}
          return;
        }

        toastMessage = `${label} succeeded • ${durationMs} ms`;
        try {
          window.dispatchEvent(
            new CustomEvent("tena:notice", {
              detail: { kind: "success", message: toastMessage },
            })
          );
        } catch {}

        if (cacheResult) {
          const payload = { meta, body };
          setHealthMeta(meta);
          writeCachedHealth(payload);
          try {
            window.localStorage.setItem("grafana:url:hint", body?.grafana_url || "");
          } catch {}
          onSavedHealth?.(meta);
        }
      } catch (error) {
        const errorText = error instanceof Error ? error.message : "Unable to complete request";
        setStatusPayload({ error: errorText });
        toastMessage = `${label} failed • ${errorText}`;
        try {
          window.dispatchEvent(
            new CustomEvent("tena:notice", {
              detail: { kind: "error", message: toastMessage },
            })
          );
        } catch {}
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
      label: `Dashboard UID ${uid.trim()}`,
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
      label: `Datasource UID ${dsUid.trim()}`,
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
      label: `Dashboard slug ${slug.trim()}`,
    });
  };

  const lastCheckDescription = useMemo(() => {
    if (!healthMeta) return "No successful check yet.";
    const relative = formatRelative(healthMeta.at);
    const latency = typeof healthMeta.durationMs === "number" ? `${healthMeta.durationMs} ms` : "";
    return `Last check: ${relative} • HTTP ${healthMeta.status}${latency ? ` • ${latency}` : ""}`;
  }, [healthMeta]);

  const detailMessage = useMemo(() => {
    if (!statusPayload) return "";
    const detail = statusPayload.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (detail && typeof detail === "object" && typeof detail.message === "string") {
      return detail.message;
    }
    if (typeof statusPayload.message === "string") {
      return statusPayload.message;
    }
    return "";
  }, [statusPayload]);

  return (
    <div className="space-y-4">
      <CollapsibleSection
        id="observability-health"
        title="Grafana connectivity"
        helper="Run the health probe before enabling dashboards in production."
        action={
          <a
            href={grafanaUrl || "/grafana"}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-primary hover:underline"
          >
            Open Grafana
          </a>
        }
      >
        <div className="space-y-4">
          <div className="rounded-lg border border-border-color bg-surface px-4 py-3 text-sm text-secondary-text">
            {lastCheckDescription}
          </div>
          <Button
            onClick={handleHealthCheck}
            disabled={isChecking}
            className="w-full"
            size="lg"
          >
            {isChecking && activeProbe === "Grafana health check" ? "Checking..." : "Run health check"}
          </Button>
        </div>
      </CollapsibleSection>

      <CollapsibleSection
        id="observability-diagnostics"
        title="Dashboard diagnostics"
        helper="Validate your Grafana identifiers before wiring widgets."
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="diagnostic-uid">
              Dashboard UID
            </label>
            <p className="text-xs text-secondary-text">Capture it from Grafana → Dashboards → Settings.</p>
            <div className="mt-2 flex flex-col gap-3 md:flex-row">
              <input
                id="diagnostic-uid"
                value={uid}
                onChange={(e) => setUid(e.target.value)}
                className={`w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                  fieldErrors.uid ? "border-red-500 ring-red-200" : "border-border-color"
                }`}
                placeholder="tenantra-overview"
              />
              <Button
                variant="ghost"
                onClick={handleUidCheck}
                disabled={isChecking}
                className="w-full md:w-auto"
              >
                {isChecking && activeProbe.startsWith("Dashboard UID") ? "Checking..." : "Check UID"}
              </Button>
            </div>
            {fieldErrors.uid && <p className="mt-2 text-xs text-red-500">{fieldErrors.uid}</p>}
          </div>

          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="diagnostic-datasource">
              Datasource UID
            </label>
            <p className="text-xs text-secondary-text">Optional, but useful when running custom Prometheus/Uptime panels.</p>
            <div className="mt-2 flex flex-col gap-3 md:flex-row">
              <input
                id="diagnostic-datasource"
                value={dsUid}
                onChange={(e) => setDsUid(e.target.value)}
                className={`w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                  fieldErrors.dsUid ? "border-red-500 ring-red-200" : "border-border-color"
                }`}
                placeholder="prometheus"
              />
              <Button
                variant="ghost"
                onClick={handleDatasourceCheck}
                disabled={isChecking}
                className="w-full md:w-auto"
              >
                {isChecking && activeProbe.startsWith("Datasource") ? "Checking..." : "Check datasource"}
              </Button>
            </div>
            {fieldErrors.dsUid && <p className="mt-2 text-xs text-red-500">{fieldErrors.dsUid}</p>}
          </div>

          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="diagnostic-slug">
              Dashboard slug
            </label>
            <p className="text-xs text-secondary-text">Slug matches the URL path (e.g., observability-overview).</p>
            <div className="mt-2 flex flex-col gap-3 md:flex-row">
              <input
                id="diagnostic-slug"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                className={`w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                  fieldErrors.slug ? "border-red-500 ring-red-200" : "border-border-color"
                }`}
                placeholder="tenantra-overview"
              />
              <Button
                variant="ghost"
                onClick={handleSlugCheck}
                disabled={isChecking}
                className="w-full md:w-auto"
              >
                {isChecking && activeProbe.startsWith("Dashboard slug") ? "Checking..." : "Check slug"}
              </Button>
            </div>
            {fieldErrors.slug && <p className="mt-2 text-xs text-red-500">{fieldErrors.slug}</p>}
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection
        id="observability-diagnostics-json"
        title="Diagnostics payload"
        helper="Raw JSON is available for deep dives and support tickets."
        defaultOpen={false}
      >
        {statusPayload ? (
          <pre className="max-h-80 overflow-auto rounded-lg bg-gray-900 p-4 text-xs text-gray-100">
            <code>{JSON.stringify(statusPayload, null, 2)}</code>
          </pre>
        ) : (
          <p className="text-xs text-secondary-text">Run a probe to populate diagnostics.</p>
        )}
        {(detailMessage === "grafana.url not configured" || statusPayload?.configured === false) && (
          <p className="mt-4 text-xs text-amber-600">
            grafana.url is missing. Navigate to Branding → Grafana integration to configure it, then re-run the health check.
          </p>
        )}
      </CollapsibleSection>
    </div>
  );
}

export default memo(ObservabilityTab);
