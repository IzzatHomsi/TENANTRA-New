import { jsx, jsxs } from "react/jsx-runtime";
import "react";
function Table({ columns, rows, empty }) {
  return /* @__PURE__ */ jsx("div", { className: "overflow-x-auto", children: /* @__PURE__ */ jsxs("table", { className: "min-w-full divide-y divide-gray-200", children: [
    /* @__PURE__ */ jsx("thead", { className: "bg-gray-50", children: /* @__PURE__ */ jsx("tr", { children: columns.map((column) => /* @__PURE__ */ jsx(
      "th",
      {
        className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500",
        children: column.label
      },
      column.key
    )) }) }),
    /* @__PURE__ */ jsx("tbody", { className: "divide-y divide-gray-200 bg-white", children: rows.length === 0 ? /* @__PURE__ */ jsx("tr", { children: /* @__PURE__ */ jsx("td", { colSpan: columns.length, className: "py-12 text-center text-gray-500", children: empty }) }) : rows.map((row, idx) => /* @__PURE__ */ jsx("tr", { children: columns.map((column) => /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: typeof column.render === "function" ? column.render(row[column.key], row) : row[column.key] ?? "-" }, column.key)) }, idx)) })
  ] }) });
}
export {
  Table as T
};
