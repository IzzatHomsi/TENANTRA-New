import React, { useEffect, useState } from "react";
import Table from "../ui/Table.jsx";
import { getApiBase } from "../../utils/apiBase";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const formatDate = (value) => {
  if (!value) return "?";
  return new Date(value).toLocaleString();
};

const renderFindingSummary = (f) => {
  const parts = [];
  parts.push(`${f.host}:${f.port} ${String(f.status || "").toUpperCase()}`);
  if (f.http) {
    const h = f.http;
    const code = h.status_code ? ` ${h.status_code}` : "";
    const srv = h.server ? ` ${h.server}` : "";
    parts.push(`[HTTP${code}${srv}]`);
  }
  if (Array.isArray(f.software) && f.software.length) {
    const s = f.software[0];
    parts.push(`[SW ${s.product}${s.version ? ` ${s.version}` : ""}]`);
  }
  if (f.tls) {
    const t = f.tls;
    const exp = typeof t.expires_in_days === "number" ? ` exp ${t.expires_in_days}d` : "";
    parts.push(`[TLS ${t.protocol || ""}${exp}]`);
  }
  return parts.join(" • ");
};

export default function ModuleRuns({ module, token }) {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (module) {
      loadRuns(module.id);
    }
  }, [module]);

  const loadRuns = async (moduleId) => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/module-runs?module_id=${moduleId}`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setRuns(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load module runs");
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "recorded_at", label: "Recorded At", render: (v) => formatDate(v) },
    { key: "status", label: "Status", render: (v) => v?.toUpperCase() ?? v },
    { key: "findings_count", label: "Findings", render: (v, row) => row.details?.findings?.length || 0 },
    { key: "details", label: "Details", render: (v) => (
      v?.findings && v.findings.length ? (
        <ul className="list-disc pl-5">
          {v.findings.slice(0, 3).map((f, i) => (
            <li key={i} title={JSON.stringify(f, null, 2)}>{renderFindingSummary(f)}</li>
          ))}
          {v.findings.length > 3 && <li>...</li>}
        </ul>
      ) : "-"
    ) },
  ];

  return (
    <div>
      <h3 className="mb-4 text-xl font-bold">Module Runs</h3>
      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}
      {loading ? (
        <p>Loading module runs...</p>
      ) : runs.length === 0 ? (
        <p>No runs recorded for this module.</p>
      ) : (
        <Table columns={columns} rows={runs} empty="No runs recorded for this module." />
      )}
    </div>
  );
}
