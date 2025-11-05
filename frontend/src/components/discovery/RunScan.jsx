import React, { useState } from "react";
import { getApiBase } from "../../utils/apiBase";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

export default function RunScan() {
  const [cidr, setCidr] = useState("");
  const [hosts, setHosts] = useState("");
  const [ports, setPorts] = useState("22,80,443");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const run = async () => {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const targetList = [];
      const parsedPorts = ports.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n) && n > 0 && n < 65536);
      if (cidr.trim()) {
        targetList.push({ host: cidr.trim(), ports: parsedPorts });
      }
      const hostList = hosts.split(/[\s,]+/).map((s) => s.trim()).filter(Boolean);
      for (const h of hostList) {
        targetList.push({ host: h, ports: parsedPorts });
      }
      if (targetList.length === 0) {
        setError("Provide a CIDR or at least one host.");
        setBusy(false);
        return;
      }
      const res = await fetch(`${API_BASE}/admin/network/port-scan`, {
        method: "POST",
        headers: authHeaders(token),
        body: JSON.stringify({ targets: targetList }),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e?.message || "Discovery failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <h2 className="mb-4 text-xl font-bold text-gray-900">Run Discovery Scan</h2>
      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">CIDR (optional)</label>
          <input
            value={cidr}
            onChange={(e) => setCidr(e.target.value)}
            placeholder="10.0.0.0/24"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Hosts (one per line or comma-separated)</label>
          <textarea
            rows={6}
            value={hosts}
            onChange={(e) => setHosts(e.target.value)}
            placeholder={"10.0.0.5\nexample.local"}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Ports</label>
          <input
            value={ports}
            onChange={(e) => setPorts(e.target.value)}
            placeholder="22,80,443"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
        </div>
        <Button onClick={run} disabled={busy}>
          {busy ? "Scanning..." : "Run Discovery"}
        </Button>
      </div>
      {result && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900">Results</h3>
          <div className="mt-4 space-y-2">
            {Array.isArray(result.findings) && result.findings.length ? (
              <ul className="space-y-2">
                {result.findings.slice(0, 20).map((f, i) => (
                  <li key={i} className="rounded-md bg-gray-100 p-3">
                    <pre className="text-sm">{JSON.stringify(f, null, 2)}</pre>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-sm text-gray-500">No findings returned.</div>
            )}
            <details className="mt-4">
              <summary className="cursor-pointer text-sm text-gray-600">Raw JSON</summary>
              <pre className="mt-2 max-h-72 overflow-auto rounded bg-gray-900 p-2 text-xs text-white">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      )}
    </Card>
  );
}
