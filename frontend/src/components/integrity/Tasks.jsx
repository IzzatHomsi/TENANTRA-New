import React from "react";
import Table from "../ui/Table.jsx";

export default function Tasks({ tasks }) {
  const columns = [
    { key: "name", label: "Name" },
    { key: "task_type", label: "Type" },
    { key: "schedule", label: "Schedule" },
    { key: "command", label: "Command" },
  ];

  return <Table columns={columns} rows={tasks} empty="No tasks found." />;
}
