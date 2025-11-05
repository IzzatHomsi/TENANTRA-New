import React from "react";
import Table from "../ui/Table.jsx";

export default function Registry({ registry, baseline }) {
  const columns = [
    { key: "hive", label: "Hive" },
    { key: "key_path", label: "Key" },
    { key: "value_name", label: "Name" },
    { key: "value_data", label: "Value" },
    { key: "value_type", label: "Type" },
  ];

  const rows = registry.map((entry) => {
    const baselineEntry = baseline.find(
      (b) =>
        b.hive?.toUpperCase() === entry.hive?.toUpperCase() &&
        b.key_path === entry.key_path &&
        b.value_name === entry.value_name
    );
    const isMismatch = baselineEntry && (
      (baselineEntry.expected_value && baselineEntry.expected_value !== entry.value_data) ||
      (baselineEntry.expected_type && baselineEntry.expected_type !== entry.value_type)
    );

    return {
      ...entry,
      isMismatch,
    };
  });

  return (
    <Table
      columns={columns}
      rows={rows}
      empty="No registry entries found."
      rowClassName={(row) => (row.isMismatch ? "bg-red-50" : "")}
    />
  );
}
