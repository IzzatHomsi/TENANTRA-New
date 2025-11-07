import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { isAdminRole } from "../utils/rbac.js";

export default function Navbar() {
  const navigate = useNavigate();
  const { user, role, signOut } = useAuth();
  const isAdmin = isAdminRole(role);

  function handleLogout() {
    signOut();
    navigate("/login", { replace: true });
  }

  return (
    <nav className="fixed top-0 left-0 flex h-screen w-64 flex-col justify-between bg-surface text-primary-text shadow-xl">
      <div className="p-5">
        <div className="text-2xl font-bold tracking-tight">Tenantra</div>
        <p className="mt-2 text-xs uppercase tracking-wide text-secondary-text">
          {user?.username || "Authenticated user"}
        </p>
        <ul className="mt-8 space-y-3 text-sm">
          <li>
            <Link to="/dashboard" className="block rounded-md px-3 py-2 transition hover:bg-neutral">
              Dashboard
            </Link>
          </li>
          {isAdmin && (
            <li>
              <Link to="/users" className="block rounded-md px-3 py-2 transition hover:bg-neutral">
                User Management
              </Link>
            </li>
          )}
          <li>
            <Link to="/compliance-trends" className="block rounded-md px-3 py-2 transition hover:bg-neutral">
              Compliance Trends
            </Link>
          </li>
          <li>
            <Link to="/profile" className="block rounded-md px-3 py-2 transition hover:bg-neutral">
              Profile
            </Link>
          </li>
          <li>
            <Link to="/notifications" className="block rounded-md px-3 py-2 transition hover:bg-neutral">
              Notifications
            </Link>
          </li>
        </ul>
      </div>
      <div className="border-t border-border-color p-5 text-sm">
        <button
          type="button"
          onClick={handleLogout}
          className="w-full rounded-md px-3 py-2 text-left font-medium text-secondary transition hover:bg-neutral hover:text-secondary"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
