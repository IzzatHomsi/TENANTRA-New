import React from "react";

export default function ModuleList({ modules, selectedId, onSelect }) {
  if (!modules.length) {
    return <div className="text-gray-500">No modules match the current filters.</div>;
  }

  return (
    <div className="max-h-[70vh] space-y-3 overflow-y-auto pr-2">
      {modules.map((module) => (
        <button
          key={module.id}
          onClick={() => onSelect(module.id)}
          className={`w-full rounded-lg border p-4 text-left ${selectedId === module.id ? "border-facebook-blue bg-blue-50" : "border-gray-200 bg-white"}`}>
          <div className="font-semibold">{module.name}</div>
          <div className="text-sm text-gray-500">
            {module.category || "Uncategorised"}
            {module.phase !== null && module.phase !== undefined ? ` • Phase ${module.phase}` : ""}
          </div>
          <div className={`text-sm ${module.enabled ? "text-green-600" : "text-red-600"}`}>
            {module.enabled ? "Enabled" : "Disabled"}
            {module.has_runner ? " • Runnable" : " • No runner"}
          </div>
        </button>
      ))}
    </div>
  );
}
