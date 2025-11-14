import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import { getApiBase } from "../utils/apiBase";

const API_BASE = getApiBase();

export default function ComplianceTrends() {
  const [days, setDays] = useState(30);
  const [trend, setTrend] = useState([]);
  const [summary, setSummary] = useState({ coverage: 0, open_failures: 0, net_change: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadInsights = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/compliance/trends/insights?days=${days}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const body = await res.json();
      setTrend(body.trend || []);
      setSummary(body.summary || { coverage: 0, open_failures: 0, net_change: 0 });
    } catch (err) {
      setError(err.message || "Failed to load compliance trends");
    } finally {
      setLoading(false);
    }
  }, [days, token]);

  useEffect(() => {
    loadInsights();
  }, [loadInsights]);

  const summaryCards = useMemo(
    () => [
      {
        title: "Overall Coverage",
        metric: `${summary.coverage?.toFixed(1) ?? "0.0"}%`,
        tone: "text-primary-text",
        hint: "Passing controls across the selected window.",
      },
      {
        title: "Open Failures",
        metric: summary.open_failures?.toLocaleString() ?? "0",
        tone: summary.open_failures > 0 ? "text-danger" : "text-success",
        hint: "Failing checks awaiting remediation.",
      },
      {
        title: `${days}-Day Net Trend`,
        metric: `${summary.net_change >= 0 ? "+" : ""}${(summary.net_change ?? 0).toFixed(1)}%`,
        tone: summary.net_change >= 0 ? "text-success" : "text-danger",
        hint: "Change in coverage versus the start of the period.",
      },
    ],
    [summary, days]
  );

  return (
    <div className="bg-neutral p-8 space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-primary-text">Compliance Trends</h1>
        <p className="mt-2 text-sm text-secondary-text">
          Track pass/fail performance for compliance modules scoped to your current tenant.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-danger/30 bg-danger/10 p-4 text-sm text-danger max-w-3xl">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {summaryCards.map(({ title, metric, hint, tone }) => (
          <Card key={title}>
            <div className={`text-4xl font-bold ${tone}`}>{metric}</div>
            <div className="mt-2 text-lg font-medium text-primary-text">{title}</div>
            <p className="mt-1 text-sm text-secondary-text">{hint}</p>
          </Card>
        ))}
      </div>

      <Card className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold text-primary-text">Pass/Fail Trend</h2>
            <p className="text-sm text-secondary-text">
              Historical coverage for the last {days} days.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="rounded-md border border-border-color bg-surface px-3 py-2 text-sm text-primary-text"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
            </select>
            <Button onClick={loadInsights} disabled={loading}>
              {loading ? "Refreshing…" : "Reload"}
            </Button>
          </div>
        </div>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trend}>
              <XAxis dataKey="date" tickFormatter={(value) => value.slice(5)} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Bar dataKey="pass" fill="var(--tena-secondary)" name="Pass" stackId="stack" />
              <Bar dataKey="fail" fill="var(--tena-danger)" name="Fail" stackId="stack" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
