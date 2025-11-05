// src/utils/rbac.js
// Purpose: normalize role values and decide if a role is admin using a single source of truth.

// 1) Normalize any incoming role string (e.g., "System Admin" -> "system_admin")
export function normalizeRole(role) {
  return (role ?? "")
    .toString()
    .trim()
    .toLowerCase()
    .replace(/^role[_:\s-]*/, "")       // drop prefixes like ROLE_, role:, etc.
    .replace(/\s+/g, "_");              // spaces -> underscores
}

// 2) Known admin synonyms (expand as needed for your backend)
const ADMIN_SET = new Set([
  "admin",
  "administrator",
  "super_admin",
  "system_admin",
  "sysadmin",
  "root",
]);

// 3) Is this role an admin?
export function isAdminRole(role) {
  return ADMIN_SET.has(normalizeRole(role));
}

// 4) Safely derive a role string from an arbitrary user object
export function deriveRoleFromUser(userLike) {
  if (!userLike) return null;
  const r =
    userLike.role ??
    userLike.role_name ??
    userLike.roleKey ??
    userLike.roleType ??
    null;
  return r ? normalizeRole(r) : null;
}
