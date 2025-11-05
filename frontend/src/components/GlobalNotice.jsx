import React from "react";

export default function GlobalNotice({ kind = "info", message = "", onClose }) {
  if (!message) return null;
  const base = "fixed top-0 left-0 right-0 z-50";
  const tone = kind === "error"
    ? "bg-red-600 text-white"
    : kind === "warn"
    ? "bg-amber-500 text-black"
    : "bg-emerald-600 text-white";
  return (
    <div className={`${base} ${tone}`} role="status">
      <div className="mx-auto max-w-7xl flex items-center justify-between px-4 py-2">
        <div className="text-sm font-medium">{message}</div>
        {onClose && (
          <button
            type="button"
            aria-label="Dismiss notification"
            className="ml-3 inline-flex h-7 w-7 items-center justify-center rounded hover:opacity-85"
            onClick={onClose}
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

