import React from "react";
import Table from "../ui/Table.jsx";

export default function Services({ services, baseline }) {
  const columns = [
    { key: "name", label: "Name" },
    { key: "status", label: "Status" },
    { key: "start_mode", label: "Start" },
    { key: "run_account", label: "Account" },
    { key: "binary_path", label: "Path" },
  ];

  const rows = services.map((service) => {
    const baselineService = baseline.find(
      (b) => b.name?.toLowerCase() === service.name?.toLowerCase()
    );
    const isMismatch = baselineService && (
      (baselineService.expected_status && baselineService.expected_status !== service.status) ||
      (baselineService.expected_start_mode && baselineService.expected_start_mode !== service.start_mode) ||
      (baselineService.expected_run_account && baselineService.expected_run_account !== service.run_account) ||
      (baselineService.expected_hash && baselineService.expected_hash !== service.hash)
    );

    return {
      ...service,
      isMismatch,
    };
  });

  return (
    <Table
      columns={columns}
      rows={rows}
      empty="No services found."
      rowClassName={(row) => (row.isMismatch ? "bg-red-50" : "")}
    />
  );
}
