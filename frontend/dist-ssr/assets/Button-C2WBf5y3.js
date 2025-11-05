import { jsx } from "react/jsx-runtime";
import "react";
const base = "btn";
const variants = {
  primary: "btn-primary",
  ghost: "btn-ghost",
  outline: "btn-outline",
  danger: "bg-red-600 text-white hover:brightness-110"
};
const sizes = {
  sm: "text-xs px-2 py-1.5",
  md: "text-sm px-3 py-2",
  lg: "text-base px-4 py-2.5"
};
function Button({
  as: Component = "button",
  children,
  className = "",
  variant = "primary",
  size = "md",
  type = "button",
  ...rest
}) {
  const v = variants[variant] || variants.primary;
  const s = sizes[size] || sizes.md;
  const cls = [base, v, s, className].filter(Boolean).join(" ");
  const props = { className: cls, ...rest };
  if (Component === "button" || Component === void 0) {
    props.type = type;
  }
  return /* @__PURE__ */ jsx(Component, { ...props, children });
}
export {
  Button as B
};
