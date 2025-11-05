import { jsx } from "react/jsx-runtime";
import "react";
function Card({ children, className = "", padded = true, ...rest }) {
  return /* @__PURE__ */ jsx("div", { className: ["card shadow-soft", padded ? "p-4" : "", className].join(" "), ...rest, children });
}
export {
  Card as C
};
