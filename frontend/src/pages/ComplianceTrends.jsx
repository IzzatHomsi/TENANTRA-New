import React from "react";
import Card from "../components/ui/Card.jsx";

const SUMMARY = [
  {
    title: "Overall Coverage",
    metric: "82%",
    hint: "Passing controls across all assets.",
  },
  {
    title: "Open Failures",
    metric: "37",
    hint: "Failing checks not yet resolved.",
  },
  {
    title: "30-Day Trend",
    metric: "+6%",
    hint: "Net improvement in pass rate.",
  },
];

export default function ComplianceTrends() {
  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Compliance Trends</h1>
        <p className="mt-2 text-sm text-gray-600">
          Track control coverage, failed checks by family, and drift over time. Scope respects tenant and RBAC filters.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {SUMMARY.map(({ title, metric, hint }) => (
          <Card key={title}>
            <div className="text-4xl font-bold text-facebook-blue">{metric}</div>
            <div className="mt-2 text-lg font-medium text-gray-900">{title}</div>
            <p className="mt-1 text-sm text-gray-600">{hint}</p>
          </Card>
        ))}
      </div>

      <div className="mt-8 rounded-lg bg-blue-100 p-6 text-sm text-blue-800">
        <p>
          Ensure all data requests enforce tenant and role filters (RBAC) before exposing production metrics.
        </p>
      </div>
    </div>
  );
}