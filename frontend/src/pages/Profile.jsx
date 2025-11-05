import React, { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";

const API_BASE = getApiBase();

export default function Profile() {
  const { token, user, role } = useAuth();

  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const isStrongPassword = (pw) => {
    if (!pw) return true;
    return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(pw);
  };

  const readErr = async (res) => {
    try {
      const text = await res.text();
      try {
        const json = JSON.parse(text);
        return json?.detail || json?.message || text;
      } catch {
        return text;
      }
    } catch {
      return `HTTP ${res.status}`;
    }
  };

  const handleSave = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");

    if (!email.trim() || !/\S+@\S+\.\S+/.test(email)) {
      setError("Please provide a valid email address.");
      return;
    }
    if (!isStrongPassword(password)) {
      setError(
        "Password must be at least 8 chars and include upper, lower, digit, and special character."
      );
      return;
    }

    const body = { email };
    if (password) body.password = password;

    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/users/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const msg = await readErr(res);
        throw new Error(msg || `Update failed (HTTP ${res.status})`);
      }

      setMessage("Profile updated successfully.");
      setPassword("");
    } catch (err) {
      setError(err.message || "Failed to update profile.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
        <p className="mt-2 text-sm text-gray-600">Update your account details and rotate credentials.</p>
      </header>

      <Card className="max-w-lg">
        {message && <div className="mb-4 rounded-md bg-green-100 p-4 text-green-700">{message}</div>}
        {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}

        <form onSubmit={handleSave} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Username</label>
            <input value={user?.username || ""} disabled className="mt-1 block w-full rounded-md border-gray-300 bg-gray-100 shadow-sm sm:text-sm" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              placeholder="you@example.com"
              onChange={(event) => setEmail(event.target.value)}
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">New Password</label>
            <input
              type="password"
              value={password}
              placeholder="Leave empty to keep current password"
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">
              Role: <strong>{role || "standard_user"}</strong>
            </span>
            <Button type="submit" disabled={submitting}>
              {submitting ? "Saving..." : "Save"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}