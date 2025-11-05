import React, { useEffect, useState, useMemo, useCallback, useRef } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Table from "../components/ui/Table.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

export default function LogViewer() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");
  const [sortBy, setSortBy] = useState("timestamp");
  const [sortOrder, setSortOrder] = useState("desc");
  const timer = useRef(null);

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/logs?limit=200`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setLogs(Array.isArray(data) ? data : data.items || []);
    } catch (e) {
      setError(e.message || "Failed to load logs");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadLogs();
    timer.current = setInterval(loadLogs, 3000);
    return () => {
      if (timer.current) {
        clearInterval(timer.current);
      }
    };
  }, [loadLogs]);

  const filteredLogs = useMemo(() => {
    return logs
      .filter((log) =>
        JSON.stringify(log).toLowerCase().includes(filter.toLowerCase())
      )
      .sort((a, b) => {
        if (a[sortBy] < b[sortBy]) return sortOrder === "asc" ? -1 : 1;
        if (a[sortBy] > b[sortBy]) return sortOrder === "asc" ? 1 : -1;
        return 0;
      });
  }, [logs, filter, sortBy, sortOrder]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const columns = [
    { key: "timestamp", label: "Timestamp" },
    { key: "level", label: "Level" },
    { key: "message", label: "Message" },
  ];

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Log Viewer</h1>
        <p className="mt-2 text-sm text-gray-600">Live tail of recent backend log lines (autorefresh every 3 seconds).</p>
      </header>

      <Card>
        <div className="mb-4">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            placeholder="Filter logs..."
          />
        </div>
        <Table
          columns={columns.map(c => ({ ...c, label: <div onClick={() => handleSort(c.key)}>{c.label} {sortBy === c.key && (sortOrder === "asc" ? "▲" : "▼")}</div> }))}
          rows={filteredLogs}
          empty="No logs found."
        />
      </Card>
    </div>
  );
}