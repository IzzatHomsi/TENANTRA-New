import React, { useEffect, useState, useCallback } from "react";
import Card from "../components/ui/Card.jsx";
import Table from "../components/ui/Table.jsx";
import { fetchNotifications } from "../api/notifications.ts";

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");
  const [sortBy, setSortBy] = useState("sent_at");
  const [sortOrder, setSortOrder] = useState("desc");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadNotifications = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchNotifications(token);
      setNotifications(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e.message || "Failed to load notifications.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  const filteredNotifications = React.useMemo(() => {
    return notifications
      .filter((notification) =>
        JSON.stringify(notification).toLowerCase().includes(filter.toLowerCase())
      )
      .sort((a, b) => {
        if (a[sortBy] < b[sortBy]) return sortOrder === "asc" ? -1 : 1;
        if (a[sortBy] > b[sortBy]) return sortOrder === "asc" ? 1 : -1;
        return 0;
      });
  }, [notifications, filter, sortBy, sortOrder]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const columns = [
    { key: "title", label: "Title" },
    { key: "message", label: "Message" },
    { key: "sent_at", label: "Sent At" },
  ];

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>
        <p className="mt-2 text-sm text-gray-600">
          System, compliance, and workflow alerts land here for quick triage.
        </p>
      </header>

      {error && (
        <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">
          {error}
        </div>
      )}

      <Card>
        <div className="mb-4">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            placeholder="Filter notifications..."
          />
        </div>
        <Table
          columns={columns.map(c => ({ ...c, label: <div onClick={() => handleSort(c.key)}>{c.label} {sortBy === c.key && (sortOrder === "asc" ? "▲" : "▼")}</div> }))}
          rows={filteredNotifications}
          empty="No notifications yet. New activity will surface here automatically."
        />
      </Card>
    </div>
  );
}
