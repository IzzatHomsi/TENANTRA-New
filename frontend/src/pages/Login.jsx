import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";

export default function Login() {
  const { signIn, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location?.state && location.state.from && location.state.from.pathname) || "/dashboard";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, from, navigate]);

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await signIn({ username, password });
      navigate(from, { replace: true });
    } catch (err) {
      setError(err?.message || "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-neutral flex min-h-screen flex-col items-center justify-center">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-primary">tenantra</h1>
          <p className="text-xl">Connect with friends and the world around you on Tenantra.</p>
        </div>
        <div className="bg-surface p-8 rounded-lg shadow-lg">
          <form onSubmit={handleLogin}>
            <ErrorBanner message={error} onClose={() => setError("")} />
            <div className="mb-4">
              <input
                className="w-full rounded-md border border-gray-300 px-4 py-3 text-lg focus:border-primary focus:outline-none"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Username"
                required
              />
            </div>
            <div className="mb-4">
              <input
                className="w-full rounded-md border border-gray-300 px-4 py-3 text-lg focus:border-primary focus:outline-none"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Password"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full rounded-md bg-primary px-4 py-3 text-lg font-bold text-white hover:bg-blue-600 disabled:opacity-60"
              disabled={submitting}
            >
              {submitting ? "Logging In..." : "Login"}
            </button>
          </form>
          <div className="text-center mt-4">
            <a href="#" className="text-primary hover:underline">
              Forgot password?
            </a>
          </div>
          <hr className="my-6" />
          <div className="text-center">
            <button className="rounded-md bg-green-500 px-6 py-3 text-lg font-bold text-white hover:bg-green-600">
              Create New Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
