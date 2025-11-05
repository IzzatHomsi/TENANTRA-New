import React, { Suspense } from "react";
import { useRoutes } from "react-router-dom";
import { routeConfig } from "./routes/routeConfig.jsx";

const fallback = <div className="p-8 text-center text-gray-500">Loading...</div>;

export default function App() {
  const element = useRoutes(routeConfig);
  return <Suspense fallback={fallback}>{element}</Suspense>;
}
