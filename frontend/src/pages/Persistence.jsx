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

const fetchPersistenceData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};

const eventColumns = [
  { key: "detected_at", label: "Detected" },
  { key: "event_type", label: "Type" },
  { key: "severity", label: "Severity" },
  { key: "title", label: "Title" },
  { key: "description", label: "Details" },
];

const registryColumns = [
  { key: "agent_id", label: "Agent" },
  { key: "hive", label: "Hive" },
  { key: "key_path", label: "Key" },
  { key: "value_name", label: "Value Name" },
  { key: "value_data", label: "Data" },
  { key: "collected_at", label: "Collected" },
];

const bootColumns = [
  { key: "agent_id", label: "Agent" },
  { key: "platform", label: "Platform" },
  { key: "config_path", label: "Path" },
  { key: "checksum", label: "Checksum" },
  { key: "collected_at", label: "Collected" },
];

const serviceColumns = [
  { key: "agent_id", label: "Agent" },
  { key: "name", label: "Service" },
  { key: "status", label: "Status" },
  { key: "start_mode", label: "Start" },
  { key: "run_account", label: "Run As" },
  { key: "collected_at", label: "Collected" },
];

const taskColumns = [
  { key: "agent_id", label: "Agent" },
  { key: "name", label: "Task" },
  { key: "task_type", label: "Type" },
  { key: "schedule", label: "Schedule" },
  { key: "command", label: "Command" },
  { key: "collected_at", label: "Collected" },
];

export default function Persistence() {
  const [agentId, setAgentId] = useState("");
  const [hive, setHive] = useState("HKLM\\SOFTWARE");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [registry, setRegistry] = useState([]);
  const [events, setEvents] = useState([]);
  const [services, setServices] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [boot, setBoot] = useState([]);

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const refreshData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const qs = agentId
        ? `agent_id=${agentId}${hive ? `&hive=${encodeURIComponent(hive)}` : ""}`
        : hive
        ? `hive=${encodeURIComponent(hive)}`
        : "";

      const [reg, evt, svc, tsk, bootResp] = await Promise.all([
        fetchPersistenceData(token, `/integrity/registry?${qs}`),
        fetchPersistenceData(token, `/integrity/events${agentId ? `?agent_id=${agentId}` : ""}`),
        fetchPersistenceData(token, `/integrity/services${agentId ? `?agent_id=${agentId}` : ""}`),
        fetchPersistenceData(token, `/integrity/tasks${agentId ? `?agent_id=${agentId}` : ""}`),
        fetchPersistenceData(token, `/integrity/boot${agentId ? `?agent_id=${agentId}` : ""}`),
      ]);
      setRegistry(reg || []);
      setEvents(evt || []);
      setServices(svc || []);
      setTasks(tsk || []);
      setBoot(bootResp || []);
    } catch (err) {
      setError(err.message || "Failed to load persistence data");
    } finally {
      setLoading(false);
    }
  }, [token, agentId, hive]);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Persistence & Integrity</h1>
        <p className="mt-2 text-sm text-gray-600">
          Track registry, boot, service, and scheduled task drift across your managed endpoints. Data refreshes automatically after agents upload snapshots.
        </p>
      </header>

      <Card className="mb-8">
        <div className="flex items-center space-x-4">
          <input
            type="number"
            placeholder="Agent ID"
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            className="w-32 rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          />
          <input
            type="text"
            placeholder="Hive filter"
            value={hive}
            onChange={(e) => setHive(e.target.value)}
            className="w-52 rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          />
          <Button onClick={refreshData} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </Card>

      {error && (
        <div className="mb-8 rounded-md bg-red-100 p-4 text-red-700">
          {error}
        </div>
      )}

      <div className="space-y-8">
        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Integrity Alerts</h2>
          <Table columns={eventColumns} rows={events} empty="No integrity drift detected." />
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Registry Snapshot</h2>
          <Table columns={registryColumns} rows={registry} empty="No registry data." />
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Boot Configurations</h2>
          <Table columns={bootColumns} rows={boot} empty="No boot configurations uploaded." />
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Services</h2>
          <Table columns={serviceColumns} rows={services} empty="No service snapshots." />
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Scheduled Tasks</h2>
          <Table columns={taskColumns} rows={tasks} empty="No scheduled task snapshots." />
        </Card>
      </div>
    </div>
  );
}