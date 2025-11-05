import React from "react";

export default function Tabs({ tabs, activeTab, setActiveTab }) {
  return (
    <div className="border-b border-border-color">
      <nav className="-mb-px flex flex-wrap gap-4 sm:flex-nowrap sm:space-x-8" aria-label="Tabs">
        {tabs.map((tab) => {
          const isActive = tab.name === activeTab;
          const base =
            "whitespace-nowrap border-b-2 py-3 px-1 text-sm font-medium transition-colors duration-200";
          const cls = isActive
            ? "border-primary text-primary"
            : "border-transparent text-secondary-text hover:border-border-color hover:text-primary-text";
          return (
            <button
              key={tab.name}
              onClick={() => setActiveTab(tab.name)}
              className={`${base} ${cls}`}
              type="button"
              aria-selected={isActive}
              aria-controls={`admin-settings-tab-${tab.name}`}
            >
              {tab.label}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
