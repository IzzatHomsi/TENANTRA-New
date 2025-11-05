import React from "react";

export default function Card({ children, className = "", padded = true, ...rest }) {
  return (
    <div className={["card shadow-soft", padded ? "p-4" : "", className].join(" ")} {...rest}>
      {children}
    </div>
  );
}

