import React from "react";
import Card from "../components/ui/Card.jsx";

export default function ObservabilitySetup() {
  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Observability Setup</h1>
      </header>

      <div className="space-y-6">
        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Grafana Connectivity</h2>
          <ol className="list-decimal space-y-2 pl-5 text-gray-700">
            <li>Go to Admin Settings → Branding and set <code>grafana.url</code> (e.g., http://localhost:3000). Save.</li>
            <li>If Grafana requires auth, set backend env vars <code>GRAFANA_USER</code> and <code>GRAFANA_PASS</code>, then restart backend.</li>
            <li>Use Admin Settings → Observability tab to Recheck health, validate a Dashboard UID (e.g., tenantra-overview), Datasource UID, and Slug.</li>
          </ol>
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Prometheus</h2>
          <ul className="list-disc space-y-2 pl-5 text-gray-700">
            <li>Ensure Prometheus is running (compose override: docker-compose.override.observability.yml).</li>
            <li>Scrape Tenantra backend metrics endpoint at <code>http://backend:5000/metrics</code> or via Nginx if exposed.</li>
          </ul>
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Common Issues</h2>
          <ul className="list-disc space-y-2 pl-5 text-gray-700">
            <li>"grafana.url not configured": set it in Branding and Save.</li>
            <li>401/403 from Grafana: set <code>GRAFANA_USER</code>/<code>GRAFANA_PASS</code>.</li>
            <li>Network access: ensure containers share the same Docker network (core).</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}