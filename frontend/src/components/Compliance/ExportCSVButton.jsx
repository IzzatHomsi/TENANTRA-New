import React from "react";

export default function ExportCSVButton({ endpoint, label = "Export CSV" }) {
  const download = () => {
    const link = document.createElement("a");
    link.href = endpoint;
    link.download = "compliance_export.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <button onClick={download} className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
      {label}
    </button>
  );
}
