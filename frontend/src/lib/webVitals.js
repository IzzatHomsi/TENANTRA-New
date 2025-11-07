import { onCLS, onINP, onLCP } from "web-vitals";
import { getApiBase } from "../utils/apiBase";

function postWebVital(payload) {
  try {
    const apiBase = getApiBase();
    const url = `${apiBase}/telemetry/web-vitals`;
    const body = JSON.stringify(payload);
    if (navigator.sendBeacon) {
      const blob = new Blob([body], { type: "application/json" });
      if (navigator.sendBeacon(url, blob)) return;
    }
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
      credentials: "include",
    }).catch(() => {});
  } catch (error) {
    // Swallow client-only telemetry issues; metrics are informational
    console.warn("[web-vitals] telemetry post failed", error);
  }
}

function resolveNavigationType() {
  try {
    const navEntry = performance?.getEntriesByType?.("navigation")?.[0];
    if (navEntry?.type) return String(navEntry.type);
    const legacyType = performance?.navigation?.type;
    if (typeof legacyType === "number") return `legacy-${legacyType}`;
    if (typeof legacyType === "string" && legacyType.trim()) return legacyType;
  } catch {
    /* ignore */
  }
  return "unknown";
}

function defaultLogger(metric) {
  if (typeof window === "undefined") return;
  try {
    const navigationType = resolveNavigationType();
    const payload = {
      name: metric.name,
      id: metric.id,
      value: Number(metric.value.toFixed(2)),
      rating: metric.rating,
      navigationType,
      timestamp: Date.now(),
      tenant: (typeof window !== "undefined" && localStorage.getItem("tenant_id")) || undefined,
      userId: (typeof window !== "undefined" && localStorage.getItem("user_id")) || undefined,
      url: (typeof window !== "undefined" && window.location.href) || undefined,
      extra: metric.attribution ? { attribution: metric.attribution } : undefined,
    };
    console.info("[web-vitals]", payload);
    postWebVital(payload);
  } catch (error) {
    console.warn("[web-vitals] unable to log metric", error);
  }
}

export function registerWebVitals(logger = defaultLogger) {
  if (typeof window === "undefined") return;
  onCLS(logger);
  onINP(logger);
  onLCP(logger);
}
