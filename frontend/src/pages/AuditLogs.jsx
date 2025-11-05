import React, { useEffect, useState, useMemo, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";

const API_BASE = getApiBase();

const authHeaders = (token, extra = {}) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
  ...extra,
});

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({
    page: 1,
    pageSize: 50,
    userId: "",
    start: "",
    end: "",
    result: "",
  });

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const qs = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          qs.set(key, value);
        }
      });

      const res = await fetch(`${API_BASE}/audit-logs?${qs.toString()}`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setLogs(data?.items || []);
      setTotal(data?.total || 0);
    } catch (e) {
      setError(e.message || "Failed to load audit logs");
    } finally {
      setLoading(false);
    }
  }, [token, filters]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value, page: 1 }));
  };

  const exportCsv = async () => {
    try {
      const qs = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value && key !== "page" && key !== "pageSize") {
          qs.set(key, value);
        }
      });

      const res = await fetch(`${API_BASE}/audit-logs/export?${qs.toString()}`, {
        headers: authHeaders(token, { Accept: "text/csv" }),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "audit_logs.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert(e?.message || "Failed to export");
    }
  };

  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / filters.pageSize)), [total, filters.pageSize]);

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Audit Logs</h1>
          <p className="mt-2 text-sm text-gray-600">Filter, review, and export platform audit logs.</p>
        </div>
        <Button onClick={exportCsv}>Export CSV</Button>
      </header>

      <Card>
        <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-5">
          <input
            name="userId"
            value={filters.userId}
            onChange={handleFilterChange}
            placeholder="User ID"
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
          <input
            type="date"
            name="start"
            value={filters.start}
            onChange={handleFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
          <input
            type="date"
            name="end"
            value={filters.end}
            onChange={handleFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
          <select
            name="result"
            value={filters.result}
            onChange={handleFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          >
            <option value="">Any result</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
            <option value="denied">Denied</option>
          </select>
          <select
            name="pageSize"
            value={filters.pageSize}
            onChange={handleFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          >
            {[25, 50, 100, 200, 500].map((n) => (
              <option key={n} value={n}>
                {n}/page
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">
            {error}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Timestamp</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Action</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Result</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">IP</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-gray-500">
                    No audit logs found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={`${log.timestamp}-${log.user_id}-${log.action}`}>
                    <td className="whitespace-nowrap px-6 py-4">{log.timestamp}</td>
                    <td className="whitespace-nowrap px-6 py-4">{log.user_id ?? "-"}</td>
                    <td className="whitespace-nowrap px-6 py-4">{log.action}</td>
                    <td className="whitespace-nowrap px-6 py-4">{log.result}</td>
                    <td className="whitespace-nowrap px-6 py-4">{log.ip || "-"}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-xs text-gray-700">{log.details || "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-500">{total} results</div>
          <div className="flex items-center space-x-2">
            <Button
              onClick={() => setFilters((prev) => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
              disabled={filters.page <= 1}
            >
              Prev
            </Button>
            <div className="text-sm">
              Page {filters.page} / {pageCount}
            </div>
            <Button
              onClick={() => setFilters((prev) => ({ ...prev, page: Math.min(pageCount, prev.page + 1) }))}
              disabled={filters.page >= pageCount}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}