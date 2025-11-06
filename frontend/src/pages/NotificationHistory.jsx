import React, { useEffect, useState, useCallback } from "react";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import Table from "../components/ui/Table.jsx";
import { fetchNotificationHistory } from "../api/notificationHistory.ts";

export default function NotificationHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({
    channel: "",
    recipient: "",
    limit: 50,
  });

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchNotificationHistory(token, filters);
      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load notification history");
    } finally {
      setLoading(false);
    }
  }, [token, filters]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: name === "limit" ? Number(value) : value,
    }));
  };

  const columns = [
    { key: "sent_at", label: "Sent" },
    { key: "channel", label: "Channel" },
    { key: "recipient", label: "Recipient" },
    { key: "subject", label: "Subject" },
    { key: "status", label: "Status" },
    { key: "error", label: "Error", render: (v) => (v ? <span className="text-red-600">{v}</span> : "-") },
  ];

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Notification History</h1>
        <p className="mt-2 text-sm text-gray-600">
          Review alerts and messages sent to tenant stakeholders with filters by channel and recipient.
        </p>
      </header>

      <Card className="mb-8">
        <div className="flex items-center space-x-4">
          <input
            name="channel"
            value={filters.channel}
            onChange={handleFilterChange}
            placeholder="Channel (email, sms, webhook)"
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
          <input
            name="recipient"
            value={filters.recipient}
            onChange={handleFilterChange}
            placeholder="Recipient"
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          />
          <select
            name="limit"
            value={filters.limit}
            onChange={handleFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          >
            {[50, 100, 200, 500, 1000].map((n) => (
              <option key={n} value={n}>
                {n} rows
              </option>
            ))}
          </select>
          <Button onClick={loadHistory} disabled={loading}>
            {loading ? "Refreshing..." : "Apply"}
          </Button>
        </div>
      </Card>

      {error && (
        <div className="mb-8 rounded-md bg-red-100 p-4 text-red-700">
          {error}
        </div>
      )}

      <Card>
        <Table columns={columns} rows={history} empty="No notifications found." />
      </Card>
    </div>
  );
}
