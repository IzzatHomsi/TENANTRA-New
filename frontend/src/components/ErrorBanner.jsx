import React from "react";

export default function ErrorBanner({ message, onClose }) {
  if (!message) return null;
  return (
    <div className="mb-3 flex items-start justify-between rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert">
      <div className="pr-3">{message}</div>
      <button
        type="button"
        aria-label="Dismiss error"
        className="ml-2 inline-flex h-6 w-6 items-center justify-center rounded hover:bg-red-100"
        onClick={onClose}
      >
        ×
      </button>
    </div>
  );
}

