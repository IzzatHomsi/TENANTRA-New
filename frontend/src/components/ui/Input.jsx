import React from "react";

export default function Input({
  as = "input",
  label,
  hint,
  className = "",
  ...rest
}) {
  const base = ["w-full rounded border px-2 py-2 field-control", className]
    .filter(Boolean)
    .join(" ");
  return (
    <label className="block text-sm">
      {label && (
        <div className="mb-1 text-gray-700 dark:text-gray-200">{label}</div>
      )}
      {as === "textarea" ? (
        <textarea className={base} {...rest} />
      ) : (
        <input className={base} {...rest} />
      )}
      {hint && <div className="mt-1 text-xs text-gray-500">{hint}</div>}
    </label>
  );
}
