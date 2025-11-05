import React from "react";

const paths = {
  bolt: "M13 3L4 14h7l-1 7 9-11h-7l1-7z",
  clock: "M12 8v5l4 2m5-3a9 9 0 11-18 0 9 9 0 0118 0z",
  shield: "M12 22s8-4 8-10V6l-8-4-8 4v6c0 6 8 10 8 10z",
  graph: "M4 19h16M7 12l3 3 7-7",
  search: "M21 21l-4.35-4.35M10 18a8 8 0 100-16 8 8 0 000 16z",
  user: "M12 14a5 5 0 100-10 5 5 0 000 10zm7 8a7 7 0 10-14 0h14z",
};

export default function Icon({ name, size = 18, className = "", stroke = 2 }) {
  const d = paths[name] || paths.graph;
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={stroke}
      strokeLinecap="round"
      strokeLinejoin="round"
      width={size}
      height={size}
      className={className}
    >
      <path d={d} />
    </svg>
  );
}

