import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getApiBase } from "../utils/apiBase";
import Button from "../components/ui/Button.jsx";

const API_BASE = getApiBase();

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState("pending");
  const [message, setMessage] = useState("Verifying your email…");
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Verification token missing.");
      return;
    }
    let cancelled = false;
    const run = async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/verify-email`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body?.detail || body?.message || "Verification failed");
        }
        const data = await res.json();
        if (cancelled) return;
        setStatus("success");
        setMessage(data?.status === "already_verified" ? "Your email was already verified." : "Email verified. You can now sign in.");
      } catch (err) {
        if (cancelled) return;
        setStatus("error");
        setMessage(err?.message || "Verification failed.");
      }
    };
    run();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="relative min-h-screen bg-[radial-gradient(circle_at_top,_rgba(79,70,229,0.18),_transparent_60%)]">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[rgba(17,24,39,0.95)] via-[rgba(17,24,39,0.8)] to-[rgba(22,163,74,0.25)]" />
      <div className="relative z-10 flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-lg rounded-3xl border border-white/30 bg-white/95 p-10 text-center shadow-[var(--tena-shadow-card)]">
          <h1 className="text-3xl font-semibold text-slate-900">Verify email</h1>
          <p className={`mt-4 text-base ${status === "error" ? "text-rose-600" : "text-slate-600"}`}>{message}</p>
          <div className="mt-6 flex justify-center">
            <Button onClick={() => navigate("/login")} className="min-w-[180px]">
              Go to login
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
