import React from "react";
import { useAuth } from "../context/AuthContext.jsx";
import RunScan from "../components/discovery/RunScan.jsx";
import CreateSchedule from "../components/discovery/CreateSchedule.jsx";
import CreateBulkSchedules from "../components/discovery/CreateBulkSchedules.jsx";

export default function Discovery() {
  const { role } = useAuth();
  const isAdmin = role === "admin" || role === "super_admin";

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Network Discovery</h1>
        <p className="mt-2 text-sm text-gray-600">
          Scan one or more hosts/ranges for open TCP ports and basic service signals.
        </p>
      </header>

      <div className="space-y-8">
        <RunScan />
        <CreateSchedule isAdmin={isAdmin} />
        <CreateBulkSchedules isAdmin={isAdmin} />
      </div>
    </div>
  );
}