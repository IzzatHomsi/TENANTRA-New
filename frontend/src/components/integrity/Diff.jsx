import React from "react";

export default function Diff({ serviceDiff, registryDiff }) {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      <div>
        <h3 className="text-lg font-medium">Service Changes</h3>
        <pre className="mt-4 overflow-auto rounded-lg bg-gray-800 p-4 text-sm text-white">
          <code>{JSON.stringify(serviceDiff, null, 2)}</code>
        </pre>
      </div>
      <div>
        <h3 className="text-lg font-medium">Registry Changes</h3>
        <pre className="mt-4 overflow-auto rounded-lg bg-gray-800 p-4 text-sm text-white">
          <code>{JSON.stringify(registryDiff, null, 2)}</code>
        </pre>
      </div>
    </div>
  );
}
