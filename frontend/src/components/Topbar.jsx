import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Topbar({ onMenu }) {
  const navigate = useNavigate();
  const { signOut, user } = useAuth();

  function handleClearSession() {
    signOut();
    navigate("/login", { replace: true });
  }

  return (
    <div className="flex items-center gap-4 border-b border-slate-200 bg-white/90 px-4 py-3 shadow-sm backdrop-blur">
      <button
        type="button"
        className="rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 md:hidden"
        onClick={() => onMenu?.()}
        aria-label="Toggle navigation menu"
      >
        ☰
      </button>
      <div className="flex-1">
        <input
          placeholder="Search…"
          className="w-full max-w-sm rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
        />
      </div>
      <div className="flex items-center gap-4 text-sm text-slate-500">
        <span>{user?.username || "User"}</span>
        <button
          type="button"
          className="rounded-md border border-slate-200 px-3 py-2 font-medium text-slate-600 transition hover:bg-slate-100"
          onClick={handleClearSession}
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
