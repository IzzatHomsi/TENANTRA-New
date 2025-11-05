import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

export default function AgentLogs() {
  const { id } = useParams();
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    axios.get(`/api/agents/${id}/logs`)
      .then(res => setLogs(res.data))
      .catch(err => console.error("Log fetch error:", err));
  }, [id]);

  return (
    <div className="bg-white rounded-xl p-4 shadow">
      <h2 className="text-lg font-semibold mb-3">Agent Logs (ID: {id})</h2>
      <div className="overflow-auto max-h-[600px]">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-4 py-2 text-left">Time</th>
              <th className="px-4 py-2 text-left">Severity</th>
              <th className="px-4 py-2 text-left">Message</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="px-4 py-1">{new Date(log.created_at).toLocaleString()}</td>
                <td className="px-4 py-1 font-semibold text-red-600">{log.severity.toUpperCase()}</td>
                <td className="px-4 py-1">{log.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
