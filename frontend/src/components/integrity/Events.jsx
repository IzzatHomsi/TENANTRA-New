import React from "react";
import Table from "../ui/Table.jsx";

export default function Events({ events }) {
  const columns = [
    { key: "detected_at", label: "Time" },
    { key: "severity", label: "Severity" },
    { key: "event_type", label: "Type" },
    { key: "title", label: "Title" },
  ];

  return <Table columns={columns} rows={events} empty="No events found." />;
}
