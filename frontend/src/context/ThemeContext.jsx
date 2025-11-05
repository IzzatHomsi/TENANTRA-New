import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

const THEME_STORAGE_KEY = "tena_theme";
const ThemeContext = createContext(null);

function readStoredTheme() {
  if (typeof window === "undefined") return "system";
  try {
    let stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (!stored) {
      const legacy = localStorage.getItem("tenat_theme");
      if (legacy) {
        stored = legacy;
        localStorage.setItem(THEME_STORAGE_KEY, legacy);
        localStorage.removeItem("tenat_theme");
      }
    }
    return stored === "light" || stored === "dark" || stored === "system" ? stored : "system";
  } catch {
    return "system";
  }
}

function applyColorScheme(mode) {
  if (typeof document === "undefined") {
    return;
  }
  const isDark = mode === "dark";
  const root = document.documentElement;
  root.classList.toggle("dark", isDark);
  root.setAttribute("data-theme", mode);
  root.style.setProperty("color-scheme", isDark ? "dark" : "light");
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => readStoredTheme());
  const [resolvedTheme, setResolvedTheme] = useState("light");

  const updateResolvedTheme = useCallback(
    (nextTheme) => {
      const prefersDark = typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      const resolved = nextTheme === "system" ? (prefersDark ? "dark" : "light") : nextTheme;
      setResolvedTheme(resolved);
      applyColorScheme(resolved);
    },
    []
  );

  useEffect(() => {
    updateResolvedTheme(theme);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      /* ignore storage failures */
    }
  }, [theme, updateResolvedTheme]);

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) {
      return;
    }
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (theme === "system") {
        updateResolvedTheme("system");
      }
    };
    media.addEventListener("change", handler);
    return () => media.removeEventListener("change", handler);
  }, [theme, updateResolvedTheme]);

  useEffect(() => {
    // Apply stored theme on initial mount (handles SSR/hydration mismatch).
    updateResolvedTheme(readStoredTheme());
  }, [updateResolvedTheme]);

  const value = useMemo(
    () => ({
      theme,
      resolvedTheme,
      setTheme: setThemeState,
    }),
    [theme, resolvedTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return ctx;
}
