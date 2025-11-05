import React from "react";

function MetadataRow({ label, value }) {
  return (
    <div className="grid grid-cols-3 gap-4 text-sm">
      <div className="text-gray-500">{label}</div>
      <div className="col-span-2">{value ?? "-"}</div>
    </div>
  );
}

function SchemaSummary({ schema }) {
  if (!schema || Object.keys(schema).length === 0) {
    return <div className="text-sm text-gray-500">This module accepts arbitrary parameters. Use JSON payloads when running manually.</div>;
  }

  const properties = Object.entries(schema.properties || {});

  return (
    <div className="space-y-4">
      {properties.length === 0 ? (
        <div className="text-sm text-gray-500">This module accepts arbitrary parameters. Use JSON payloads when running manually.</div>
      ) : (
        properties.map(([key, descriptor]) => (
          <div key={key} className="rounded-md border p-4">
            <div className="font-semibold">{key}</div>
            <div className="mt-1 text-sm text-gray-600">{descriptor.description || "No description provided."}</div>
            {descriptor.type && <div className="mt-2 text-xs text-gray-500">Type: {descriptor.type}</div>}
            {Array.isArray(descriptor.enum) && (
              <div className="mt-2 text-xs text-gray-500">Allowed values: {descriptor.enum.join(", ")}</div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default function ModuleDetails({ module, onToggleEnabled }) {
  if (!module) {
    return <div className="text-gray-500">Select a module to view details.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">{module.name}</h2>
          <div className="text-sm text-gray-500">
            {module.category || "Uncategorised"}
            {module.phase !== null && module.phase !== undefined ? ` • Phase ${module.phase}` : ""}
          </div>
        </div>
        <button
          onClick={() => onToggleEnabled(module)}
          className={`rounded-md px-4 py-2 text-sm font-medium ${module.enabled ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`}>
          {module.enabled ? "Disable" : "Enable"}
        </button>
      </div>

      <div className="space-y-4">
        <MetadataRow label="Impact" value={module.impact_level} />
        <MetadataRow label="Purpose" value={module.purpose || module.description} />
        <MetadataRow label="Dependencies" value={module.dependencies} />
        <MetadataRow label="Preconditions" value={module.preconditions} />
        <MetadataRow label="Team" value={module.team} />
        <MetadataRow label="Targets" value={module.application_target} />
        <MetadataRow label="Supported OS" value={module.operating_systems} />
        <MetadataRow label="Compliance" value={module.compliance_mapping} />
        <MetadataRow label="Last update" value={new Date(module.last_update).toLocaleString()} />
        <MetadataRow label="Runner available" value={module.has_runner ? "Yes" : "No"} />
      </div>

      <div>
        <h3 className="mb-4 text-xl font-bold">Parameter Schema</h3>
        <SchemaSummary schema={module.parameter_schema} />
      </div>
    </div>
  );
}
