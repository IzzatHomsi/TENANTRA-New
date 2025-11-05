import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const navigate = useNavigate();
  const { signIn } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleLogin(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await signIn({ username, password });
      navigate("/app/dashboard", { replace: true });
    } catch (err) {
      setError(err?.message || "Invalid username or password");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <form onSubmit={handleLogin} className="w-full max-w-md rounded-xl bg-white p-8 shadow">
        <h2 className="text-center text-2xl font-semibold text-slate-900">Login to Tenantra</h2>

        <label className="mt-6 block text-sm font-medium text-slate-700">
          Username
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-2 text-sm focus:border-emerald-500 focus:outline-none"
            required
          />
        </label>

        <label className="mt-4 block text-sm font-medium text-slate-700">
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-2 text-sm focus:border-emerald-500 focus:outline-none"
            required
          />
        </label>

        {error && <p className="mt-3 text-sm text-red-500">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="mt-6 w-full rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {submitting ? "Signing in..." : "Login"}
        </button>
      </form>
    </div>
  );
}
