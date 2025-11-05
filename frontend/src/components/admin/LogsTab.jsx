import React, { useEffect, useState, useCallback } from "react";
import Button from "../ui/Button.jsx";

export default function LogsTab({ headers }) {
  const [lines, setLines] = useState([]);
  const [path, setPath] = useState("");
  const [error, setError] = useState("");
  const [auto, setAuto] = useState(true);
  const [intervalMs, setIntervalMs] = useState(3000);

  const refresh = useCallback(async () => {
    setError("");
    try {
      const r = await fetch("/api/admin/app/logs", { headers });
      if (r.ok) {
        const j = await r.json();
        setLines(j.lines || []);
        setPath(j.path || "");
      } else {
        const j = await r.json().catch(() => ({ detail: `HTTP ${r.status}` }));
        setError(j.detail || `HTTP ${r.status}`);
      }
    } catch (e) {
      setError(String(e));
    }
  }, [headers]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!auto) return;
    const id = setInterval(refresh, Math.max(1000, intervalMs));
    return () => clearInterval(id);
  }, [auto, intervalMs, refresh]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-primary-text">
          App Logs (tail){path ? ` — ${path}` : ""}
        </h3>
        <div className="flex items-center space-x-4">
          <label className="flex items-center text-sm">
            <input
              type="checkbox"
              checked={auto}
              onChange={(e) => setAuto(e.target.checked)}
              className="h-4 w-4 rounded border-border-color text-primary focus:ring-primary"
            />
            <span className="ml-2">Auto-refresh</span>
          </label>
          <input
            type="number"
            min="1000"
            step="500"
            value={intervalMs}
            onChange={(e) => setIntervalMs(Number(e.target.value) || 3000)}
            className="w-24 rounded-md border border-border-color px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
          <Button onClick={refresh}>Refresh</Button>
        </div>
      </div>
      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error} {error.includes("not found") && "(check LOG_FILE_PATH and backend log path)"}
        </div>
      )}
      <pre className="max-h-96 overflow-auto rounded-lg bg-gray-900 p-4 text-sm text-green-400">
        <code>{lines.join("\n")}</code>
      </pre>
    </div>
  );
}
