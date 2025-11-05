import React from "react";
import Button from "../ui/Button.jsx";

export default function RegistryBaseline({ baseline, setBaseline, onSave }) {
  const addRow = () => {
    setBaseline([
      ...baseline,
      {
        hive: "HKLM",
        key_path: "",
        value_name: "",
        expected_value: "",
        expected_type: "",
        is_critical: false,
        notes: "",
      },
    ]);
  };

  const removeRow = (index) => {
    setBaseline(baseline.filter((_, i) => i !== index));
  };

  const handleChange = (index, field, value) => {
    const newBaseline = [...baseline];
    newBaseline[index][field] = value;
    setBaseline(newBaseline);
  };

  return (
    <div>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Registry Baseline</h3>
        <div className="flex space-x-4">
          <Button onClick={addRow}>Add</Button>
          <Button onClick={onSave}>Save</Button>
        </div>
      </div>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Hive</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Key</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Expected Value</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Critical</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Notes</th>
              <th className="relative px-6 py-3">
                <span className="sr-only">Remove</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {baseline.map((row, index) => (
              <tr key={index}>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={row.hive || ""}
                    onChange={(e) => handleChange(index, "hive", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={row.key_path || ""}
                    onChange={(e) => handleChange(index, "key_path", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={row.value_name || ""}
                    onChange={(e) => handleChange(index, "value_name", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={row.expected_value || ""}
                    onChange={(e) => handleChange(index, "expected_value", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={row.expected_type || ""}
                    onChange={(e) => handleChange(index, "expected_type", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    type="checkbox"
                    checked={!!row.is_critical}
                    onChange={(e) => handleChange(index, "is_critical", e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <input
                    value={row.notes || ""}
                    onChange={(e) => handleChange(index, "notes", e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
                  />
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                  <Button variant="ghost" onClick={() => removeRow(index)}>
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
