import React, { useEffect, useState } from "react";
import axios from "axios";
import ExportCSVButton from "./ExportCSVButton";

export default function ComplianceTable() {
  const [records, setRecords] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    axios.get("/api/compliance/results").then((res) => {
      setRecords(res.data);
    });
  }, []);

  const filtered = filter === "all" ? records : records.filter(r => r.status === filter);

  return (
    <div className="bg-white rounded-xl p-4 shadow mt-6">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-semibold">Compliance Scan Results</h2>
        <ExportCSVButton endpoint="/api/compliance/export.csv" />
        <select value={filter} onChange={(e) => setFilter(e.target.value)} className="border px-2 py-1 rounded">
          <option value="all">All</option>
          <option value="pass">Pass</option>
          <option value="fail">Fail</option>
        </select>
      </div>
      <div className="overflow-auto max-h-[500px]">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-4 py-2 text-left">Agent</th>
              <th className="px-4 py-2 text-left">Module</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2 text-left">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r, i) => (
              <tr key={i} className={r.status === "fail" ? "bg-red-50" : "bg-green-50"}>
                <td className="px-4 py-1">{r.agent_name}</td>
                <td className="px-4 py-1">{r.module_name}</td>
                <td className="px-4 py-1 font-semibold">{r.status.toUpperCase()}</td>
                <td className="px-4 py-1">{new Date(r.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
