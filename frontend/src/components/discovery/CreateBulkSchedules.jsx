import React, { useState } from "react";
import { getApiBase } from "../../utils/apiBase";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

export default function CreateBulkSchedules({ isAdmin }) {
  const [bulkText, setBulkText] = useState("");
  const [bulkMsg, setBulkMsg] = useState("");
  const [error, setError] = useState("");
  const [ports, setPorts] = useState("22,80,443");
  const [cron, setCron] = useState("*/30 * * * *");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const createBulkSchedules = async () => {
    setBulkMsg("");
    setError("");
    if (!isAdmin) {
      setError("Admin only");
      return;
    }
    const lines = bulkText.split(/\n+/).map((s) => s.trim()).filter(Boolean);
    if (!lines.length) {
      setError("Provide one or more lines: tenant_id=cidr1;cidr2");
      return;
    }
    try {
      let modules = await fetch(`${API_BASE}/modules/`, { headers: authHeaders(token) }).then(res => res.json());
      let mod = (modules || []).find(m => (m.external_id||'').toLowerCase() === 'port-scan' || /port\s*scan/i.test(m.name||''));
      if (!mod) {
        try {
          await fetch(`${API_BASE}/admin/modules/create-port-scan`, { method: "POST", headers: authHeaders(token) });
        } catch {}
        modules = await fetch(`${API_BASE}/modules/`, { headers: authHeaders(token) }).then(res => res.json());
        mod = (modules || []).find(m => (m.external_id||'').toLowerCase() === 'port-scan' || /port\s*scan/i.test(m.name||''));
      }
      if (!mod) {
        setError("Port Scan module not available.");
        return;
      }
      const parsedPorts = ports.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n) && n > 0 && n < 65536);
      let created = 0,
        errors = 0;
      for (const line of lines) {
        const [lhs, rangesRaw] = line.split("=");
        const [tidPart, aidPart] = (lhs || "").split(":");
        const tid = Number((tidPart || "").trim());
        const aid = aidPart ? Number(aidPart.trim()) : null;
        if (!tid || !rangesRaw) {
          errors++;
          continue;
        }
        const ranges = rangesRaw.split(/;| |\s+/).map((s) => s.trim()).filter(Boolean);
        if (!ranges.length) {
          errors++;
          continue;
        }
        const targets = ranges.map((r) => ({ host: r, ports: parsedPorts }));
        try {
          const payload = { module_id: mod.id, cron_expr: cron.trim() || "*/30 * * * *", tenant_id: tid, parameters: { targets } };
          if (aid && !isNaN(aid) && aid > 0) {
            payload.agent_id = aid;
          }
          await fetch(`${API_BASE}/schedules`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
          created++;
        } catch {
          errors++;
        }
      }
      setBulkMsg(`Created ${created} schedules${errors ? `, ${errors} failed` : ""}`);
      setTimeout(() => setBulkMsg(""), 3000);
    } catch (e) {
      setError(e?.message || "Bulk creation failed");
    }
  };

  if (!isAdmin) {
    return null;
  }

  return (
    <Card>
      <h2 className="mb-4 text-xl font-bold text-gray-900">Bulk Per-Tenant Schedules</h2>
      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}
      {bulkMsg && <div className="mb-4 rounded-md bg-green-100 p-4 text-green-700">{bulkMsg}</div>}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Tenant Schedules (one per line: tenant_id=cidr1;cidr2)</label>
          <textarea
            rows={6}
            value={bulkText}
            onChange={(e) => setBulkText(e.target.value)}
            placeholder={"1=10.0.1.0/24;10.0.2.0/24\n2=192.168.1.0/24"}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Ports</label>
            <input
              value={ports}
              onChange={(e) => setPorts(e.target.value)}
              placeholder="22,80,443"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Cron expression</label>
            <input
              value={cron}
              onChange={(e) => setCron(e.target.value)}
              placeholder="*/30 * * * *"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </div>
        </div>
        <Button onClick={createBulkSchedules}>Create Schedules</Button>
      </div>
    </Card>
  );
}
