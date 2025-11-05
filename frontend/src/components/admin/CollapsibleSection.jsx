import React, { useState } from "react";

export default function CollapsibleSection({ id, title, helper, defaultOpen = true, children, action }) {
  const [open, setOpen] = useState(defaultOpen);
  const sectionId = id || `collapsible-${title?.toLowerCase().replace(/\s+/g, "-")}`;

  return (
    <section className="rounded-xl border border-border-color bg-gray-50 p-4">
      <header className="flex items-start justify-between gap-3">
        <button
          type="button"
          className="flex flex-1 items-center justify-between text-left"
          onClick={() => setOpen((prev) => !prev)}
          aria-expanded={open}
          aria-controls={`${sectionId}-content`}
        >
          <div>
            <h3 className="text-base font-semibold text-primary-text">{title}</h3>
            {helper && <p className="mt-1 text-sm text-secondary-text">{helper}</p>}
          </div>
          <svg
            className={`h-5 w-5 text-secondary-text transition-transform ${open ? "rotate-180" : ""}`}
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path d="M6 8l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        {action ? <div className="hidden sm:block">{action}</div> : null}
      </header>
      {action ? <div className="mt-3 sm:hidden">{action}</div> : null}
      <div id={`${sectionId}-content`} className={`mt-4 space-y-4 text-sm ${open ? "block" : "hidden"}`} aria-hidden={!open}>
        {open ? children : null}
      </div>
    </section>
  );
}
