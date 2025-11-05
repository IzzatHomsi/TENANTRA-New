import React, { useState, useEffect } from "react";
import Button from "../ui/Button.jsx";

export default function RunModule({ module, onRun, runError, runMessage, runBusy }) {
  const [useForm, setUseForm] = useState(true);
  const [formValues, setFormValues] = useState({});
  const [runPayload, setRunPayload] = useState("{}");

  useEffect(() => {
    if (!module) {
      setFormValues({});
      return;
    }
    const props = (module.parameter_schema && module.parameter_schema.properties) || {};
    const init = {};
    Object.entries(props).forEach(([key, desc]) => {
      if (desc && typeof desc === "object" && "default" in desc) {
        init[key] = desc.default;
      } else {
        init[key] = "";
      }
    });
    setFormValues(init);
    try {
      setRunPayload(JSON.stringify(init, null, 2));
    } catch {}
  }, [module]);

  const handleRun = () => {
    let payload;
    try {
      if (useForm) {
        payload = { ...formValues };
      } else {
        payload = runPayload.trim() ? JSON.parse(runPayload) : {};
      }
    } catch (err) {
      onRun(null, "Parameters must be valid JSON.");
      return;
    }
    onRun(payload);
  };

  return (
    <div>
      <h3 className="mb-4 text-xl font-bold">Run Module</h3>
      <div className="mb-4 flex items-center">
        <input
          type="checkbox"
          checked={useForm}
          onChange={(e) => setUseForm(e.target.checked)}
          className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
        />
        <label className="ml-2 text-sm text-gray-700">Use parameter form</label>
      </div>
      {useForm && module?.parameter_schema?.properties ? (
        <div className="mb-4 space-y-4">
          {Object.entries(module.parameter_schema.properties).map(([key, descriptor]) => (
            <div key={key}>
              <label className="block text-sm font-medium text-gray-700">
                {key} {descriptor?.type ? <span className="text-gray-500">({descriptor.type})</span> : null}
              </label>
              <input
                value={formValues[key] ?? ""}
                onChange={(e) => {
                  const v = e.target.value;
                  const next = { ...formValues, [key]: descriptor?.type === "number" ? Number(v) : v };
                  setFormValues(next);
                  try {
                    setRunPayload(JSON.stringify(next, null, 2));
                  } catch {}
                }}
                placeholder={descriptor?.description || ""}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
          ))}
        </div>
      ) : (
        <textarea
          value={runPayload}
          onChange={(e) => setRunPayload(e.target.value)}
          rows={8}
          className="w-full rounded-md border-gray-300 font-mono text-sm shadow-sm focus:border-primary focus:ring-primary"
        />
      )}
      {runError && <div className="mt-4 rounded-md bg-red-100 p-4 text-red-700">{runError}</div>}
      {runMessage && <div className="mt-4 rounded-md bg-green-100 p-4 text-green-700">{runMessage}</div>}
      <div className="mt-4 flex space-x-4">
        <Button onClick={handleRun} disabled={runBusy}>
          {runBusy ? "Running..." : "Execute now"}
        </Button>
      </div>
    </div>
  );
}
