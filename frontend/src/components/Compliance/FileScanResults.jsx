import React, { useEffect, useState } from "react";
import ExportCSVButton from "./ExportCSVButton";
import axios from "axios";

export default function FileScanResults() {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    axios.get("/api/scans/files").then((res) => setRecords(res.data));
  }, []);

  return (
    <div className="bg-white rounded-xl p-4 shadow">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-semibold">File Scan Results</h2>
        <ExportCSVButton endpoint="/api/scans/files/export.csv" />
      </div>
      <div className="overflow-auto max-h-[600px]">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 text-left">Agent</th>
              <th className="px-4 py-2 text-left">Path</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2 text-left">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id}>
                <td className="px-4 py-1">{r.agent_id}</td>
                <td className="px-4 py-1">{r.path}</td>
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
