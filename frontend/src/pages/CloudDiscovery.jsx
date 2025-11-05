import React, { useEffect, useState, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import Table from "../components/ui/Table.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const fetchCloudData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};

export default function CloudDiscovery() {
  const [accounts, setAccounts] = useState([]);
  const [assets, setAssets] = useState([]);
  const [filters, setFilters] = useState({ provider: "", account: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [accResp, assetResp] = await Promise.all([
        fetchCloudData(token, "/cloud/accounts", { provider: filters.provider }),
        fetchCloudData(token, "/cloud/assets", { provider: filters.provider, account_id: filters.account }),
      ]);
      setAccounts(accResp || []);
      setAssets(assetResp || []);
    } catch (err) {
      setError(err.message || "Failed to load cloud inventory");
    } finally {
      setLoading(false);
    }
  }, [token, filters]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Cloud & Hybrid Discovery</h1>
        <p className="mt-2 text-sm text-gray-600">
          Visualize connected cloud accounts and discovered resources across AWS, Azure, and GCP tenants.
        </p>
      </header>

      <Card className="mb-8">
        <div className="flex items-center space-x-4">
          <select
            name="provider"
            value={filters.provider}
            onChange={handleFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          >
            <option value="">All providers</option>
            <option value="aws">AWS</option>
            <option value="azure">Azure</option>
            <option value="gcp">GCP</option>
          </select>
          <input
            name="account"
            value={filters.account}
            onChange={handleFilterChange}
            placeholder="Account ID"
            className="w-48 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
          <Button onClick={loadData} disabled={loading}>
            {loading ? "Refreshing..." : "Apply"}
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
          <h2 className="mb-4 text-xl font-bold text-gray-900">Accounts</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {accounts.length === 0 ? (
              <div className="text-sm text-gray-500">No cloud accounts connected.</div>
            ) : (
              accounts.map((account) => (
                <div key={account.id} className="rounded-lg bg-white p-4 shadow">
                  <div className="text-sm font-medium text-gray-900">{account.account_identifier}</div>
                  <div className="mt-1 text-xs text-gray-500">{account.provider?.toUpperCase()}</div>
                  <div className="mt-2 text-xs text-gray-500">Status: {account.status}</div>
                  <div className="text-xs text-gray-500">Last Sync: {account.last_synced_at || "Never"}</div>
                  <p className="mt-2 text-xs text-gray-500">{account.notes || ""}</p>
                </div>
              ))
            )}
          </div>
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Discovered Assets</h2>
          <Table
            columns={[
              { key: "account_id", label: "Account" },
              { key: "name", label: "Name" },
              { key: "asset_type", label: "Type" },
              { key: "region", label: "Region" },
              { key: "status", label: "Status" },
              { key: "metadata", label: "Metadata" },
            ]}
            rows={assets}
            empty="No assets discovered for this filter."
          />
        </Card>
      </div>
    </div>
  );
}