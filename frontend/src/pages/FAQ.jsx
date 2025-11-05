import React from "react";
import Card from "../components/ui/Card.jsx";

const FAQ_DATA = [
  {
    question: "Where do I start?",
    answer: "Bring the stack up from `docker/` with `docker compose up -d`. Frontend runs on `http://localhost:8080`, backend on `http://localhost:5000`. Default admin is `admin`/`Admin@1234`.",
  },
  {
    question: "Configuring Observability",
    answer: (
      <ul className="list-disc space-y-2 pl-5">
        <li>Set `grafana.url` under Admin Settings → Branding and Save.</li>
        <li>If required, set backend env `GRAFANA_USER` and `GRAFANA_PASS` and restart backend.</li>
        <li>Use Observability tab to verify health, dashboard UID, datasource UID, and slug.</li>
      </ul>
    ),
  },
  {
    question: "Networking — Port Scan",
    answer: (
      <>
        <p>Use Module Catalog → Quick Action to run a TCP port scan. Backend admin API:</p>
        <pre className="mt-2 overflow-auto rounded-lg bg-gray-800 p-4 text-sm text-white"><code>{`POST /api/admin/network/port-scan
{
  "host": "10.0.0.5",
  "ports": [22,80,443]
}`}</code></pre>
      </>
    ),
  },
  {
    question: "Control Menu",
    answer: "Run `tenantra_control_menu.bat`. Actions stream logs live and show status badges. Use [6] to rebuild, [2]/[3] to start, [5] to clean volumes.",
  },
  {
    question: "Cleanup",
    answer: "Preview: `tools/cleanup_report.ps1`. Apply: `tools/cleanup_report.ps1 -Apply`.",
  },
];

export default function FAQ() {
  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Frequently Asked Questions (FAQ)</h1>
      </header>

      <div className="space-y-6">
        {FAQ_DATA.map((item, index) => (
          <Card key={index}>
            <h2 className="mb-4 text-xl font-bold text-gray-900">{item.question}</h2>
            <div className="text-sm text-gray-700">{item.answer}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}