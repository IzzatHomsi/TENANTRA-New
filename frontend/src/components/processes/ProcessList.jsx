import React from "react";
import Table from "../ui/Table.jsx";

const processColumns = [
  { key: "pid", label: "PID" },
  { key: "process_name", label: "Process" },
  { key: "username", label: "User" },
  { key: "executable_path", label: "Path" },
  { key: "hash", label: "SHA256" },
  {
    key: "command_line",
    label: "Command",
    render: (value) => (value ? <code className="text-xs font-mono">{value}</code> : "-"),
  },
  { key: "collected_at", label: "Collected" },
];

export default function ProcessList({ processes, onUseAsBaseline }) {
  return (
    <div>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Active Processes</h3>
        <button onClick={onUseAsBaseline} disabled={!processes.length} className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm">
          Use snapshot as baseline
        </button>
      </div>
      <div className="mt-4">
        <Table columns={processColumns} rows={processes} empty="No process snapshot available." />
      </div>
    </div>
  );
}
