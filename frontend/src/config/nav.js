// Centralized navigation config for the sidebar.
// Each item can be:
// - a link: { type: "item", to, label, roles, enabled }
// - a section with children: { type: "section", label, children: [ ... ] }
// - a divider: { type: "divider" }
//
// roles: array of roles that can see the item. Omit or [] => all roles.
// enabled: boolean or function({ role, features }) to dynamically enable.
// features: optional feature flags (from BE or env) used by enabled().

export const NAV_CONFIG = [
  {
    type: "section",
    label: "Overview",
    children: [
      { type: "item", to: "/app/dashboard", label: "Dashboard" },
      { type: "item", to: "/app/profile", label: "My Profile" },
    ],
  },

  { type: "divider" },

  {
    type: "section",
    label: "Compliance",
    children: [
      // You said these pages exist in your project
      { type: "item", to: "/app/compliance-trends", label: "Compliance Trends" },
      { type: "item", to: "/app/notifications", label: "Notifications" },
      // Optional pages: enable them later by adding routes/pages
      {
        type: "item",
        to: "/app/compliance/results",
        label: "Compliance Results",
        enabled: ({ features }) => Boolean(features?.complianceResults),
      },
      {
        type: "item",
        to: "/app/notification-history",
        label: "Notification History",
        enabled: ({ features }) => Boolean(features?.notificationHistory),
      },
    ],
  },

  {
    type: "section",
    label: "Runtime Integrity",
    children: [
      { type: "item", to: "/app/process-monitoring", label: "Process Monitoring" },
      { type: "item", to: "/app/persistence", label: "Persistence" },
      {
        type: "item",
        to: "/app/threat-intel",
        label: "Threat Intelligence",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.threatIntel ?? true),
      },
    ],
  },

  {
    type: "section",
    label: "Assets & Scans",
    children: [
      {
        type: "item",
        to: "/app/assets",
        label: "Assets",
        enabled: ({ features }) => Boolean(features?.assets),
      },
      {
        type: "item",
        to: "/app/scan-schedules",
        label: "Scan Schedules",
        enabled: ({ features }) => Boolean(features?.scanSchedules),
      },
      {
        type: "item",
        to: "/app/reports",
        label: "Reports",
        enabled: ({ features }) => Boolean(features?.reports),
      },
      {
        type: "item",
        to: "/app/audit-logs",
        label: "Audit Logs",
        enabled: ({ features }) => Boolean(features?.auditLogs),
      },
    ],
  },

  { type: "divider" },

  {
    type: "section",
    label: "Administration",
    children: [
      // Only admins see Users/Tenants/Billing
      {
        type: "item",
        to: "/app/users",
        label: "Users",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
      },
      {
        type: "item",
        to: "/app/tenants",
        label: "Tenants",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.tenants),
      },
      {
        type: "item",
        to: "/app/billing",
        label: "Billing",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.billing),
      },
      {
        type: "item",
        to: "/app/settings",
        label: "Settings",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.settings),
      },
    ],
  },
];

// Example local feature flags for dev (can be replaced by /features API bootstrap)
export function getLocalFeatures() {
  // Toggle these on/off to reveal menu items without code changes.
  return {
    // already existing pages:
    complianceResults: false,
    notificationHistory: false,

    // optional domains:
    assets: false,
    scanSchedules: false,
    reports: false,
    auditLogs: false,
    threatIntel: true,

    tenants: false,
    billing: false,
    settings: false,
  };
}
