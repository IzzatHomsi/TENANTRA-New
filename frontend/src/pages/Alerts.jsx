import React, { useEffect, useState, useMemo } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(`${API_BASE}/alerts`, { headers: authHeaders(token) });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        setAlerts(Array.isArray(data) ? data : data.items || []);
      } catch (e) {
        setError(e.message || "Failed to load alerts.");
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, [token]);

  const filteredAlerts = useMemo(() => {
    return alerts
      .filter((alert) =>
        alert.name.toLowerCase().includes(filter.toLowerCase())
      )
      .sort((a, b) => {
        if (a[sortBy] < b[sortBy]) return sortOrder === "asc" ? -1 : 1;
        if (a[sortBy] > b[sortBy]) return sortOrder === "asc" ? 1 : -1;
        return 0;
      });
  }, [alerts, filter, sortBy, sortOrder]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-facebook-gray">
        <p>Loading alerts...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center bg-facebook-gray">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
      </header>

      <Card>
        <div className="mb-4">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            placeholder="Filter alerts..."
          />
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  className="cursor-pointer px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
                  onClick={() => handleSort("name")}
                >
                  Name {sortBy === "name" && (sortOrder === "asc" ? "▲" : "▼")}
                </th>
                <th
                  className="cursor-pointer px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
                  onClick={() => handleSort("status")}
                >
                  Status {sortBy === "status" && (sortOrder === "asc" ? "▲" : "▼")}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={2} className="py-12 text-center text-gray-500">
                    No alerts found.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alert, i) => (
                  <tr key={alert.id || i}>
                    <td className="whitespace-nowrap px-6 py-4">{alert.name || alert.rule || "Alert"}</td>
                    <td className="whitespace-nowrap px-6 py-4">{alert.status || ""}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}