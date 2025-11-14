import React, { useEffect, useState, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import Table from "../components/ui/Table.jsx";
import { useUIStore } from "../store/uiStore";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const withTenantQuery = (endpoint, tenantId) => {
  if (!tenantId) return endpoint;
  const joiner = endpoint.includes("?") ? "&" : "?";
  return `${endpoint}${joiner}tenant_id=${encodeURIComponent(tenantId)}`;
};

const fetchRetentionData = async (token, tenantId, endpoint, options = {}) => {
  const res = await fetch(`${API_BASE}${withTenantQuery(endpoint, tenantId)}`, { headers: authHeaders(token), ...options });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};

export default function RetentionExports() {
  const [policy, setPolicy] = useState(null);
  const [exports, setExports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [retentionDays, setRetentionDays] = useState(90);
  const [archive, setArchive] = useState("vault");
  const [formats, setFormats] = useState("csv,json,pdf,zip");
  const [exportType, setExportType] = useState("alerts");
  const [exportFormats, setExportFormats] = useState("csv,json");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const tenantId = useUIStore((state) => state.tenantId);

  const loadData = useCallback(async () => {
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const [policyResp, exportResp] = await Promise.all([
        fetchRetentionData(token, tenantId, "/retention/policy"),
        fetchRetentionData(token, tenantId, "/retention/exports"),
      ]);
      setPolicy(policyResp);
      setRetentionDays(policyResp?.retention_days ?? 90);
      setArchive(policyResp?.archive_storage ?? "vault");
      setFormats((policyResp?.export_formats || []).join(",") || "csv,json,pdf,zip");
      setExports(exportResp || []);
    } catch (err) {
      setError(err.message || "Failed to load retention data");
    } finally {
      setLoading(false);
    }
  }, [tenantId, token]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const updatePolicy = async () => {
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const update = {
        retention_days: Number(retentionDays),
        archive_storage: archive,
        export_formats: formats.split(",").map((f) => f.trim()).filter(Boolean),
      };
      const resp = await fetchRetentionData(token, tenantId, "/retention/policy", { method: "PUT", body: JSON.stringify(update) });
      setPolicy(resp);
      setMessage("Retention policy updated.");
    } catch (err) {
      setError(err.message || "Failed to update retention policy");
    } finally {
      setLoading(false);
    }
  };

  const requestExport = async () => {
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const formatsList = exportFormats.split(",").map((f) => f.trim()).filter(Boolean);
      const resp = await fetchRetentionData(token, tenantId, "/retention/exports", { method: "POST", body: JSON.stringify({ export_type: exportType, formats: formatsList }) });
      setExports((prev) => [resp, ...prev]);
      setMessage("Export queued and completed. Download via storage URI.");
    } catch (err) {
      setError(err.message || "Failed to request export");
    } finally {
      setLoading(false);
    }
  };

  const exportColumns = [
    { key: "requested_at", label: "Requested" },
    { key: "export_type", label: "Type" },
    { key: "formats", label: "Formats", render: (v) => (Array.isArray(v) ? v.join(", ") : v) },
    { key: "status", label: "Status" },
    { key: "storage_uri", label: "Storage URI", render: (v) => v ? <code className="text-xs">{v}</code> : "-" },
  ];

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Retention & Exports</h1>
          <p className="mt-2 text-sm text-gray-600">
            Configure tenant retention policies and generate exports for auditors, regulators, or downstream analysis.
          </p>
        </div>
        <Button onClick={loadData} disabled={loading}>
          {loading ? "Refreshing..." : "Reload"}
        </Button>
      </header>

      {message && <div className="mb-4 rounded-md bg-green-100 p-4 text-green-700">{message}</div>}
      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Retention Policy</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Retention Days</label>
              <input
                type="number"
                min={30}
                max={1825}
                value={retentionDays}
                onChange={(e) => setRetentionDays(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Archive Storage Tier</label>
              <input
                value={archive}
                onChange={(e) => setArchive(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Allowed Export Formats (comma separated)</label>
              <input
                value={formats}
                onChange={(e) => setFormats(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <Button onClick={updatePolicy} disabled={loading}>
              Update Policy
            </Button>
          </div>
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Request Export</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Export Type</label>
              <input
                value={exportType}
                onChange={(e) => setExportType(e.target.value)}
                placeholder="Export type (e.g. alerts)"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Formats (comma separated)</label>
              <input
                value={exportFormats}
                onChange={(e) => setExportFormats(e.target.value)}
                placeholder="Formats"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <Button onClick={requestExport} disabled={loading}>
              Request Export
            </Button>
          </div>
        </Card>
      </div>

      <div className="mt-8">
        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Exports</h2>
          <Table columns={exportColumns} rows={exports} empty="No exports generated yet." />
        </Card>
      </div>
    </div>
  );
}
