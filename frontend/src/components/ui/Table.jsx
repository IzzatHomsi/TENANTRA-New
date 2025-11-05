import React from "react";

export default function Table({ columns, rows, empty }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="py-12 text-center text-gray-500">
                {empty}
              </td>
            </tr>
          ) : (
            rows.map((row, idx) => (
              <tr key={idx}>
                {columns.map((column) => (
                  <td key={column.key} className="whitespace-nowrap px-6 py-4">
                    {typeof column.render === "function"
                      ? column.render(row[column.key], row)
                      : row[column.key] ?? "-"}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
