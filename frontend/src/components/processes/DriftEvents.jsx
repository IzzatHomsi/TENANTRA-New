import React from "react";
import Table from "../ui/Table.jsx";

const driftColumns = [
  { key: "detected_at", label: "Detected" },
  { key: "change_type", label: "Change" },
  { key: "process_name", label: "Process" },
  { key: "severity", label: "Severity" },
  {
    key: "details",
    label: "Details",
    render: (value) => (value ? value : "-"),
  },
];

export default function DriftEvents({ drift }) {
  const driftSummary = React.useMemo(() => {
    if (!drift.length) return "No drift events detected.";
    const counts = drift.reduce((acc, evt) => {
      acc[evt.change_type] = (acc[evt.change_type] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(counts)
      .map(([change, count]) => `${change}: ${count}`)
      .join(" | ");
  }, [drift]);

  return (
    <div>
      <h3 className="text-lg font-medium">Drift Events</h3>
      <p className="mt-1 text-sm text-gray-600">{driftSummary}</p>
      <div className="mt-4">
        <Table columns={driftColumns} rows={drift} empty="No drift events recorded." />
      </div>
    </div>
  );
}
