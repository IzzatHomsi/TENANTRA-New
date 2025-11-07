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
      { type: "item", to: "/dashboard", label: "Dashboard" },
      { type: "item", to: "/profile", label: "My Profile" },
    ],
  },

  { type: "divider" },

  {
    type: "section",
    label: "Compliance",
    children: [
      // You said these pages exist in your project
      { type: "item", to: "/compliance-trends", label: "Compliance Trends" },
      { type: "item", to: "/notifications", label: "Notifications" },
      // Optional pages: enable them later by adding routes/pages
      {
        type: "item",
        to: "/compliance/results",
        label: "Compliance Results",
        enabled: ({ features }) => Boolean(features?.complianceResults),
      },
      {
        type: "item",
        to: "/notification-history",
        label: "Notification History",
        enabled: ({ features }) => Boolean(features?.notificationHistory),
      },
    ],
  },

  {
    type: "section",
    label: "Runtime Integrity",
    children: [
      { type: "item", to: "/process-monitoring", label: "Process Monitoring" },
      { type: "item", to: "/persistence", label: "Persistence" },
      {
        type: "item",
        to: "/threat-intel",
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
        to: "/assets",
        label: "Assets",
        enabled: ({ features }) => Boolean(features?.assets),
      },
      {
        type: "item",
        to: "/scan-schedules",
        label: "Scan Schedules",
        enabled: ({ features }) => Boolean(features?.scanSchedules),
      },
      {
        type: "item",
        to: "/reports",
        label: "Reports",
        enabled: ({ features }) => Boolean(features?.reports),
      },
      {
        type: "item",
        to: "/audit-logs",
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
        to: "/users",
        label: "Users",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
      },
      {
        type: "item",
        to: "/tenants",
        label: "Tenants",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.tenants),
      },
      {
        type: "item",
        to: "/billing",
        label: "Billing",
        roles: ["admin", "administrator", "super_admin", "system_admin"],
        enabled: ({ features }) => Boolean(features?.billing),
      },
      {
        type: "item",
        to: "/settings",
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
