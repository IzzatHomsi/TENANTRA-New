import React, { useEffect, useState, useMemo, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import Table from "../components/ui/Table.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

export default function ComplianceMatrix() {
  const [matrix, setMatrix] = useState({ frameworks: [], rules: [] });
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadMatrix = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/compliance-matrix/matrix`, { headers: authHeaders(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setMatrix(data ?? { frameworks: [], rules: [] });
    } catch (err) {
      setError(err.message || "Failed to load compliance matrix");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadMatrix();
  }, [loadMatrix]);

  const filteredRules = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return matrix.rules;
    return matrix.rules.filter((rule) =>
      [rule.control_id, rule.title, rule.description, rule.category]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(term))
    );
  }, [matrix.rules, search]);

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Compliance Matrix</h1>
        <p className="mt-2 text-sm text-gray-600">
          Explore Tenantra controls mapped to major regulatory frameworks including ISO 27001, NIST CSF, HIPAA, PCI-DSS, GDPR, and CIS.
        </p>
      </header>

      <Card className="mb-8">
        <div className="flex items-center justify-between">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search controls..."
            className="w-full max-w-md rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          />
          <Button onClick={loadMatrix} disabled={loading}>
            {loading ? "Refreshing..." : "Reload"}
          </Button>
        </div>
      </Card>

      {error && (
        <div className="mb-8 rounded-md bg-red-100 p-4 text-red-700">
          {error}
        </div>
      )}

      <div className="space-y-8">
        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Frameworks</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {matrix.frameworks.length === 0 ? (
              <div className="text-sm text-gray-500">No frameworks configured.</div>
            ) : (
              matrix.frameworks.map((fw) => (
                <div key={fw.id} className="rounded-lg bg-white p-4 shadow">
                  <div className="text-sm font-medium text-gray-900">{fw.name}</div>
                  <div className="mt-1 text-xs text-gray-500">{fw.code}</div>
                  <p className="mt-2 text-xs text-gray-500">{fw.description || "No description"}</p>
                  {fw.category && <div className="mt-2 text-xs text-gray-700">Category: {fw.category}</div>}
                </div>
              ))
            )}
          </div>
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Controls</h2>
          <Table
            columns={[
              { key: "control_id", label: "Control" },
              { key: "title", label: "Title" },
              {
                key: "framework_ids",
                label: "Frameworks",
                render: (framework_ids) =>
                  framework_ids
                    .map((fid) => matrix.frameworks.find((fw) => fw.id === fid)?.code || fid)
                    .join(", ") || "-",
              },
              { key: "category", label: "Category" },
              { key: "description", label: "Description" },
            ]}
            rows={filteredRules}
            empty="No controls match this query."
          />
        </Card>
      </div>
    </div>
  );
}