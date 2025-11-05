import React, { useEffect, useState, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Icon from "../components/ui/Icon.jsx";
import { useTheme } from "../context/ThemeContext.jsx";

const EMPTY = { value: "-", hint: "", icon: "graph" };

const REFRESH_INTERVAL = parseInt(import.meta.env.VITE_DASHBOARD_REFRESH_INTERVAL || "15000", 10);

const fetchApiLatency = async () => {
  try {
    const t0 = performance.now();
    await fetch(`${getApiBase()}/health`, { cache: "no-store" });
    const t1 = performance.now();
    const ms = Math.max(1, Math.round(t1 - t0));
    return { value: `${ms}ms`, hint: "API ping latency", icon: "clock" };
  } catch {
    return { value: "n/a", hint: "API not reachable", icon: "clock" };
  }
};

const fetchAuthStatus = async () => {
  try {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const res = await fetch(`${getApiBase()}/auth/me`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
    return { value: res.ok ? "OK" : String(res.status), hint: "Auth session status", icon: "shield" };
  } catch {
    return { value: "n/a", hint: "Auth check failed", icon: "shield" };
  }
};

const fetchGrafanaHealth = async () => {
  try {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const res = await fetch(`/api/admin/observability/grafana/health`, { cache: "no-store", headers: token ? { Authorization: `Bearer ${token}` } : {} });
    return { value: res.ok ? "OK" : String(res.status), hint: "Grafana /api/health via backend", icon: "bolt" };
  } catch {
    return { value: "n/a", hint: "Grafana not reachable", icon: "bolt" };
  }
};

export default function Dashboard() {
  const { resolvedTheme } = useTheme();
  const [grafanaUrl, setGrafanaUrl] = useState("");
  const [dashUid, setDashUid] = useState("");
  const [dsUid, setDsUid] = useState("");
  const [cards, setCards] = useState({
    apiLatency: { ...EMPTY, hint: "API ping latency" },
    authStatus: { ...EMPTY, hint: "Auth session status", icon: "shield" },
    grafana: { ...EMPTY, hint: "Grafana health", icon: "bolt" },
  });

  const refreshAll = useCallback(async () => {
    const [apiLatency, authStatus, grafana] = await Promise.all([
      fetchApiLatency(),
      fetchAuthStatus(),
      fetchGrafanaHealth(),
    ]);
    setCards({ apiLatency, authStatus, grafana });
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${getApiBase()}/support/settings/public`);
        if (res.ok) {
          const j = await res.json();
          setGrafanaUrl(j["grafana.url"] || "");
          setDashUid(j["grafana.dashboard_uid"] || "");
          setDsUid(j["grafana.datasource_uid"] || "");
        }
      } catch {}
    })();

    refreshAll();
    const intervalId = setInterval(refreshAll, REFRESH_INTERVAL);

    return () => clearInterval(intervalId);
  }, [refreshAll]);

  const canEmbed = grafanaUrl && dashUid;
  const iframeSrc = canEmbed
    ? `${grafanaUrl.replace(/\/$/, "")}/d/${encodeURIComponent(dashUid)}?orgId=1&kiosk=tv&theme=${resolvedTheme === "dark" ? "dark" : "light"}${dsUid ? `&var-datasource=${encodeURIComponent(dsUid)}` : ""}`
    : "";

  return (
    <div className="space-y-6 bg-facebook-gray p-6">
      <header className="border-b border-gray-200 pb-4">
        <div className="text-xs uppercase tracking-wide text-gray-500">Overview</div>
        <h1 className="mt-1 text-2xl font-bold text-gray-900">Operations Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Welcome to Tenantra. Your tenant health snapshot updates as data sources sync and telemetry streams in.
        </p>
      </header>

      {canEmbed ? (
        <Card padded={false} className="overflow-hidden rounded-lg shadow-lg">
          <iframe title="Grafana Dashboard" src={iframeSrc} className="w-full h-[520px] border-0" />
        </Card>
      ) : (
        <Card className="border-yellow-400 bg-yellow-100 text-yellow-800">
          <div className="text-sm">To view live metrics, set Grafana URL and Dashboard UID in Admin Settings. Optionally set Datasource UID.</div>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="bg-facebook-white rounded-lg shadow-lg">
          <div className="flex items-start gap-4">
            <div className="rounded-full bg-blue-100 p-3 text-facebook-blue">
              <Icon name="clock" />
            </div>
            <div>
              <div className="text-3xl font-bold text-gray-900">{cards.apiLatency.value}</div>
              <div className="mt-1 text-base font-medium text-gray-700">API Latency</div>
              <p className="mt-2 text-sm text-gray-500">{cards.apiLatency.hint}</p>
            </div>
          </div>
        </Card>
        <Card className="bg-facebook-white rounded-lg shadow-lg">
          <div className="flex items-start gap-4">
            <div className="rounded-full bg-green-100 p-3 text-green-600">
              <Icon name="shield" />
            </div>
            <div>
              <div className="text-3xl font-bold text-gray-900">{cards.authStatus.value}</div>
              <div className="mt-1 text-base font-medium text-gray-700">Auth Status</div>
              <p className="mt-2 text-sm text-gray-500">{cards.authStatus.hint}</p>
            </div>
          </div>
        </Card>
        <Card className="bg-facebook-white rounded-lg shadow-lg">
          <div className="flex items-start gap-4">
            <div className="rounded-full bg-purple-100 p-3 text-purple-600">
              <Icon name="bolt" />
            </div>
            <div>
              <div className="text-3xl font-bold text-gray-900">{cards.grafana.value}</div>
              <div className="mt-1 text-base font-medium text-gray-700">Grafana</div>
              <p className="mt-2 text-sm text-gray-500">{cards.grafana.hint}</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
