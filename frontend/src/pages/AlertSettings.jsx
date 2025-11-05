import React, { useEffect, useState, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const EVENT_LABELS = {
  scan_failed: "Scan Failed",
  compliance_violation: "Compliance Violation",
  agent_offline: "Agent Offline",
  threshold_breach: "Threshold Breach",
};

export default function AlertSettings() {
  const [channels, setChannels] = useState({ email: true, webhook: false });
  const [events, setEvents] = useState({
    scan_failed: true,
    compliance_violation: true,
    agent_offline: true,
    threshold_breach: false,
  });
  const [digest, setDigest] = useState("immediate");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  useEffect(() => {
    const fetchPrefs = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(`${API_BASE}/notification-prefs`, { headers: authHeaders(token) });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        if (data) {
          setChannels(data.channels || { email: true, webhook: false });
          setEvents(data.events || { scan_failed: true, compliance_violation: true, agent_offline: true, threshold_breach: false });
          setDigest(data.digest || "immediate");
        }
      } catch (e) {
        setError(e.message || "Failed to load preferences");
      } finally {
        setLoading(false);
      }
    };

    fetchPrefs();
  }, [token]);

  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/notification-prefs`, {
        method: "PUT",
        headers: authHeaders(token),
        body: JSON.stringify({ channels, events, digest }),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
    } catch (e) {
      setError(e.message || "Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-neutral">
        <p>Loading alert settings...</p>
      </div>
    );
  }

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Alert Settings</h1>
        <p className="mt-2 text-sm text-gray-600">Manage notification channels, event triggers, and digest preferences.</p>
      </header>

      {error && (
        <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">
          {error}
        </div>
      )}

      <Card className="space-y-8">
        <div>
          <h3 className="text-lg font-medium leading-6 text-gray-900">Channels</h3>
          <div className="mt-4 space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={channels.email}
                onChange={(e) => setChannels({ ...channels, email: e.target.checked })}
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <span className="ml-2 text-sm text-gray-700">Email</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={channels.webhook}
                onChange={(e) => setChannels({ ...channels, webhook: e.target.checked })}
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <span className="ml-2 text-sm text-gray-700">Webhook</span>
            </label>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium leading-6 text-gray-900">Events</h3>
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            {Object.keys(events).map((key) => (
              <label key={key} className="flex items-center">
                <input
                  type="checkbox"
                  checked={events[key]}
                  onChange={(e) => setEvents({ ...events, [key]: e.target.checked })}
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <span className="ml-2 text-sm text-gray-700">
                  {EVENT_LABELS[key] || key.replace(/_/g, " ")}
                </span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium leading-6 text-gray-900">Digest</h3>
          <select
            value={digest}
            onChange={(e) => setDigest(e.target.value)}
            className="mt-4 block w-full max-w-xs rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          >
            <option value="immediate">Immediate</option>
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
          </select>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Preferences"}
          </Button>
        </div>
      </Card>
    </div>
  );
}