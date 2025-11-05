import React from "react";
import { ThemeProvider } from "./context/ThemeContext.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { QueryClientProvider } from "@tanstack/react-query";

export function AppProviders({ children, queryClient }) {
  if (!queryClient) {
    throw new Error("AppProviders requires a queryClient instance.");
  }

  return (
    <ThemeProvider>
      <AuthProvider>
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
