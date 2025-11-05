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

const fetchBillingData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};

export default function Billing() {
  const [plans, setPlans] = useState([]);
  const [usage, setUsage] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [filters, setFilters] = useState({ metric: "", status: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [planData, usageData, invoiceData] = await Promise.all([
        fetchBillingData(token, "/billing/plans"),
        fetchBillingData(token, "/billing/usage", { metric: filters.metric }),
        fetchBillingData(token, "/billing/invoices", { status: filters.status }),
      ]);
      setPlans(planData || []);
      setUsage(usageData || []);
      setInvoices(invoiceData || []);
    } catch (err) {
      setError(err.message || "Failed to load billing data");
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
        <h1 className="text-3xl font-bold text-gray-900">Usage & Billing</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitor tenant consumption metrics, subscription plans, and invoice history for MSP billing automation.
        </p>
      </header>

      <Card className="mb-8">
        <div className="flex items-center space-x-4">
          <input
            name="metric"
            value={filters.metric}
            onChange={handleFilterChange}
            placeholder="Metric filter"
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          >
            <option value="">All invoices</option>
            <option value="pending">Pending</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
          </select>
          <Button onClick={loadData} disabled={loading}>
            {loading ? "Loading..." : "Refresh"}
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
          <h2 className="mb-4 text-xl font-bold text-gray-900">Billing Plans</h2>
          <Table
            columns={[
              { key: "code", label: "Code" },
              { key: "name", label: "Plan" },
              {
                key: "base_rate",
                label: "Base Rate",
                render: (v, row) => `${row.currency || "USD"} ${v?.toFixed?.(2) ?? v}`,
              },
              {
                key: "overage_rate",
                label: "Overage",
                render: (v, row) => `${row.currency || "USD"} ${v?.toFixed?.(2) ?? v}`,
              },
              { key: "description", label: "Description" },
            ]}
            rows={plans}
            empty="No billing plans configured."
          />
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Usage Metrics</h2>
          <Table
            columns={[
              { key: "recorded_at", label: "Recorded" },
              { key: "metric", label: "Metric" },
              { key: "quantity", label: "Quantity" },
              { key: "window_start", label: "Window Start" },
              { key: "window_end", label: "Window End" },
            ]}
            rows={usage}
            empty="No usage recorded for the selected filters."
          />
        </Card>

        <Card>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Invoices</h2>
          <Table
            columns={[
              { key: "period_start", label: "Period Start" },
              { key: "period_end", label: "Period End" },
              {
                key: "amount",
                label: "Amount",
                render: (v, row) => `${row.currency || "USD"} ${v?.toFixed?.(2) ?? v}`,
              },
              { key: "status", label: "Status", render: (v) => v?.toUpperCase?.() ?? v },
              { key: "issued_at", label: "Issued" },
              { key: "due_at", label: "Due" },
              { key: "paid_at", label: "Paid" },
              { key: "notes", label: "Notes" },
            ]}
            rows={invoices}
            empty="No invoices found."
          />
        </Card>
      </div>
    </div>
  );
}