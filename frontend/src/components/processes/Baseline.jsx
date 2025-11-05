import React from "react";
import Button from "../ui/Button.jsx";

export default function Baseline({ baseline, setBaseline, onSave, scopeLabel }) {
  const addBaselineEntry = () => {
    setBaseline([
      ...baseline,
      {
        process_name: "",
        executable_path: "",
        expected_hash: "",
        expected_user: "",
        is_critical: false,
        notes: "",
      },
    ]);
  };

  const removeBaselineEntry = (index) => {
    setBaseline(baseline.filter((_, idx) => idx !== index));
  };

  const updateBaselineEntry = (index, field, value) => {
    setBaseline(
      baseline.map((entry, idx) => (idx === index ? { ...entry, [field]: value } : entry))
    );
  };

  const toggleCritical = (index) => {
    setBaseline(
      baseline.map((entry, idx) =>
        idx === index ? { ...entry, is_critical: !entry.is_critical } : entry
      )
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">{scopeLabel} Baseline</h3>
        <div className="flex space-x-4">
          <Button onClick={addBaselineEntry}>Add entry</Button>
          <Button onClick={onSave}>Save baseline</Button>
        </div>
      </div>
      <p className="mt-1 text-sm text-gray-600">
        Define expected processes, hashes, and critical entries. Baselines are evaluated when agents post new reports.
      </p>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Process</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Path</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Expected hash</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Expected user</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Critical</th>
              <th className="relative px-6 py-3">
                <span className="sr-only">Remove</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {baseline.map((entry, index) => (
              <tr key={index}>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={entry.process_name}
                    placeholder="process.exe"
                    onChange={(e) => updateBaselineEntry(index, "process_name", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={entry.executable_path}
                    placeholder="/usr/bin/process"
                    onChange={(e) => updateBaselineEntry(index, "executable_path", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={entry.expected_hash}
                    placeholder="sha256..."
                    onChange={(e) => updateBaselineEntry(index, "expected_hash", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={entry.expected_user}
                    placeholder="SYSTEM"
                    onChange={(e) => updateBaselineEntry(index, "expected_user", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    type="checkbox"
                    checked={entry.is_critical}
                    onChange={() => toggleCritical(index)}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                  <Button variant="ghost" onClick={() => removeBaselineEntry(index)}>
                    Remove
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
