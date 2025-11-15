import React, { useEffect, useState, useMemo } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import { useTheme } from "../context/ThemeContext.jsx";

const API_BASE = getApiBase();

const buildGrafanaUrl = (base, dashUid, options = {}) => {
  const params = new URLSearchParams({
    orgId: 1,
    ...options,
  });
  return `${base.replace(/\/$/, "")}/d/${encodeURIComponent(dashUid)}?${params.toString()}`;
};

export default function Metrics() {
  const { resolvedTheme } = useTheme();
  const [grafanaUrl, setGrafanaUrl] = useState("");
  const [dashUid, setDashUid] = useState("");
  const [dsUid, setDsUid] = useState("");
  const [panelIds, setPanelIds] = useState("2,4,6");
  const [warnings, setWarnings] = useState([]);
  const [warningsError, setWarningsError] = useState("");

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
      } catch {}
    })();
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadWarnings() {
      try {
        const res = await fetch(`${API_BASE}/admin/observability/grafana/warnings`);
        if (!res.ok) {
          if (res.status === 403 || res.status === 404) {
            if (!cancelled) {
              setWarnings([]);
              setWarningsError("");
            }
            return;
          }
          throw new Error(`HTTP ${res.status}`);
        }
        const payload = await res.json();
        if (!cancelled) {
          setWarnings(Array.isArray(payload?.items) ? payload.items : []);
          setWarningsError("");
        }
      } catch (err) {
        if (!cancelled) {
          setWarnings([]);
          setWarningsError(err?.message || "Unable to load Grafana warnings");
        }
      }
    }
    loadWarnings();
    const interval = setInterval(loadWarnings, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const canEmbed = grafanaUrl && dashUid;
  const panelIdList = useMemo(() => panelIds.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n)), [panelIds]);
  const warningActive = warnings.length > 0 || warningsError;

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Metrics</h1>
        <p className="mt-2 text-sm text-gray-600">Embedded Grafana dashboard and optional panels.</p>
      </header>

      {warningActive && (
        <Card className="mb-8 border border-amber-200 bg-amber-50/70">
          <div className="flex flex-col gap-3 text-amber-800">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide">Grafana warnings detected</p>
              <p className="text-sm text-amber-700">loadDashboardScene issues are surfaced here so you do not have to inspect the browser console.</p>
            </div>
            {warningsError ? (
              <p className="text-sm text-amber-700">{warningsError}</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {warnings.slice(0, 4).map((entry, idx) => (
                  <li key={`${entry.timestamp}-${idx}`} className="rounded-xl border border-amber-200 bg-white/60 px-4 py-3 text-amber-900">
                    <p className="font-semibold">
                      {entry.tag === "grafana.loadDashboardScene" ? "loadDashboardScene" : entry.tag?.replace("grafana.", "") || "proxy"} · {entry.status}
                    </p>
                    <p className="text-xs text-amber-700">{entry.message || "Grafana proxy reported an error."}</p>
                    <p className="text-xs text-amber-600">{new Date(entry.timestamp * 1000).toLocaleString()} · {entry.path}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Card>
      )}

      {!canEmbed ? (
        <Card>
          <p className="text-center text-gray-500">Set Grafana URL and Dashboard UID in Admin Settings to render metrics here.</p>
        </Card>
      ) : (
        <div className="space-y-8">
          <Card>
           <iframe
             title="Grafana Dashboard"
              src={buildGrafanaUrl(grafanaUrl, dashUid, { kiosk: "tv", theme: resolvedTheme === "dark" ? "dark" : "light", ...(dsUid && { "var-datasource": dsUid }) })}
              className="h-[520px] w-full rounded-lg border-0"
            />
          </Card>

          <Card>
            <h2 className="mb-4 text-xl font-bold text-gray-900">Embed Individual Panels</h2>
            <input
              value={panelIds}
              onChange={(e) => setPanelIds(e.target.value)}
              placeholder="Panel IDs (comma-separated), e.g., 2,4,6"
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
            <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
              {panelIdList.map((id) => (
                <div key={id} className="overflow-hidden rounded-lg shadow">
                  <iframe
                    title={`Panel ${id}`}
                    src={buildGrafanaUrl(grafanaUrl, dashUid, { theme: resolvedTheme === "dark" ? "dark" : "light", viewPanel: id, ...(dsUid && { "var-datasource": dsUid }) })}
                    className="h-[360px] w-full border-0"
                  />
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
