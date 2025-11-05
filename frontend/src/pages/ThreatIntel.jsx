import React, { useEffect, useState, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import Table from "../components/ui/Table.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const fetchThreatData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};

export default function ThreatIntel() {
  const [feeds, setFeeds] = useState([]);
  const [hits, setHits] = useState([]);
  const [severity, setSeverity] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [feedData, hitData] = await Promise.all([
        fetchThreatData(token, "/threat-intel/feeds"),
        fetchThreatData(token, "/threat-intel/hits", { severity }),
      ]);
      setFeeds(feedData || []);
      setHits(hitData || []);
    } catch (err) {
      setError(err.message || "Failed to load threat intelligence data");
    } finally {
      setLoading(false);
    }
  }, [token, severity]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const feedColumns = [
    { key: "name", label: "Name" },
    { key: "source", label: "Source" },
    { key: "feed_type", label: "Type" },
    { key: "enabled", label: "Status", render: (v) => (v ? "Enabled" : "Disabled") },
    { key: "last_synced_at", label: "Last Sync" },
  ];

  const hitColumns = [
    { key: "detected_at", label: "Detected" },
    { key: "indicator_value", label: "Indicator" },
    { key: "indicator_type", label: "Type" },
    { key: "entity_type", label: "Entity", render: (v, row) => `${v}${row.entity_identifier ? ` (${row.entity_identifier})` : ""}` },
    { key: "severity", label: "Severity", render: (v) => v?.toUpperCase() ?? v },
    { key: "context", label: "Context" },
  ];

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Threat Intelligence</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitor IoC feeds and correlate inbound indicators with tenant assets. Severity filters help prioritise urgent activity.
        </p>
      </header>

      <Card className="mb-8">
        <div className="flex items-center space-x-4">
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          >
            <option value="">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <Button onClick={loadData} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </Card>

      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}

      <div className="space-y-8">
        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Feeds</h2>
          <Table columns={feedColumns} rows={feeds} empty="No feeds configured." />
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Detections</h2>
          <Table columns={hitColumns} rows={hits} empty="No threat intelligence hits found." />
        </Card>
      </div>
    </div>
  );
}