import React, { useMemo } from "react";
import { NavLink } from "react-router-dom";
import { NAV_CONFIG, getLocalFeatures } from "../config/nav.js";
import { useAuth } from "../context/AuthContext.jsx";

function normalizeRole(role) {
  return (role ?? "").toLowerCase();
}

function isItemVisible(item, role, features) {
  if (item.enabled === false) return false;
  if (typeof item.enabled === "function") {
    try {
      if (!item.enabled({ role, features })) return false;
    } catch {
      return false;
    }
  } else if (item.enabled != null && !item.enabled) {
    return false;
  }

  if (Array.isArray(item.roles) && item.roles.length > 0) {
    const normalized = normalizeRole(role);
    return item.roles.some((allowed) => normalizeRole(allowed) === normalized);
  }

  return true;
}

function buildStructure(role, features) {
  const structure = [];

  NAV_CONFIG.forEach((entry, index) => {
    if (entry.type === "divider") {
      structure.push({ type: "divider", key: `divider-${index}` });
      return;
    }

    if (entry.type === "section") {
      const visibleItems = (entry.children || []).filter((child) =>
        child.type === "item" && isItemVisible(child, role, features)
      );

      if (visibleItems.length === 0) return;

      structure.push({
        type: "section",
        key: `section-${index}`,
        label: entry.label,
        items: visibleItems,
      });
      return;
    }

    if (entry.type === "item" && isItemVisible(entry, role, features)) {
      structure.push({ type: "item", key: `item-${index}`, item: entry });
    }
  });

  return structure
    .filter(Boolean)
    .filter((entry, idx, arr) => {
      if (entry.type !== "divider") return true;
      const prev = arr[idx - 1];
      const next = arr[idx + 1];
      if (!prev || !next) return false; // drop leading/trailing dividers
      return prev.type !== "divider" && next.type !== "divider";
    });
}

function ItemLink({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `block rounded-md px-3 py-2 text-sm transition ${
          isActive
            ? "bg-primary text-white font-semibold"
            : "text-secondary-text hover:bg-neutral hover:text-primary-text"
        }`
      }
    >
      {children}
    </NavLink>
  );
}

export default function Sidebar({ open = true, onClose, features: featureOverrides }) {
  const { role } = useAuth();

  const mergedFeatures = useMemo(() => ({
    ...getLocalFeatures(),
    ...(featureOverrides || {}),
  }), [featureOverrides]);

  const sections = useMemo(
    () => buildStructure(role, mergedFeatures),
    [role, mergedFeatures]
  );

  return (
    <>
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform border-r border-border-color bg-surface p-5 shadow-soft transition-transform duration-200 ease-in-out md:static md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`
        aria-label="Sidebar navigation"
      >
        <div className="flex items-center justify-between">
          <p className="text-lg font-semibold text-primary-text">Tenantra</p>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1 text-secondary-text hover:bg-neutral hover:text-primary-text md:hidden"
            aria-label="Close navigation"
          >
            ✕
          </button>
        </div>

        <nav className="mt-8 space-y-6">
          {sections.map((entry) => {
            if (entry.type === "divider") {
              return <div key={entry.key} className="border-t border-border-color" />;
            }

            if (entry.type === "item") {
              return (
                <div key={entry.key}>
                  <ItemLink to={entry.item.to}>{entry.item.label}</ItemLink>
                </div>
              );
            }

            return (
              <div key={entry.key}>
                <p className="text-xs font-semibold uppercase tracking-wide text-secondary-text">
                  {entry.label}
                </p>
                <div className="mt-2 space-y-1">
                  {entry.items.map((item) => (
                    <ItemLink key={item.to} to={item.to}>
                      {item.label}
                    </ItemLink>
                  ))}
                </div>
              </div>
            );
          })}
        </nav>
      </aside>

      {open && (
        <button
          type="button"
          onClick={onClose}
          className="fixed inset-0 z-30 bg-neutral/40 backdrop-blur-sm md:hidden"
          aria-label="Close sidebar overlay"
        />
      )}
    </>
  );
}
