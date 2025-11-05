// frontend/src/utils/roleUtils.js
// PURPOSE: Normalize roles from ANY auth/user shape so UI gating is consistent.
// This file exports two helpers:
//   1) deriveRoles(authLike) → Set<string>     (robust: accepts auth object OR user object)
//   2) hasRole(authLike, required) → boolean   (true if user has any of the required roles)

/* Helper (internal): add a value to a Set if it's a non-empty string. */
function _addStr(set, v) {
  // convert any value to string and trim spaces (e.g., " admin ")
  const s = (v ?? "").toString().trim();
  if (s) set.add(s); // only add if non-empty after trim
}

/* Helper (internal): add many possible role containers to the Set. */
function _collectFrom(set, container) {
  // If it's a string like "admin", add it
  if (typeof container === "string") {
    _addStr(set, container);
    return;
  }
  // If it's an array like ["admin","standard_user"], add each
  if (Array.isArray(container)) {
    container.filter(Boolean).forEach((r) => _addStr(set, r));
    return;
  }
  // If it's an object, try common keys recursively (very defensive)
  if (container && typeof container === "object") {
    // Common fields across apps
    const candidates = [
      container.role,
      container.roles,
      container.userRole,
      container.userRoles,
      container.claims?.role,
      container.session?.user?.role,
      container.session?.user?.roles,
      container.user?.role,
      container.user?.roles,
      container.profile?.role,
      container.profile?.roles,
    ];
    candidates.forEach((c) => _collectFrom(set, c));
  }
}

/**
 * Public: derive a normalized Set of role strings from any "auth-like" or "user-like" object.
 * - Accepts: { role: "admin" } OR { roles: ["admin"] } OR { user:{role:"admin"}} OR {claims:{role:["admin"]}} etc.
 * - Returns a Set with unique, trimmed roles (e.g., Set("admin","standard_user")).
 */
export function deriveRoles(authLike) {
  const roles = new Set(); // result container with unique role names
  if (!authLike) return roles; // no input → empty set
  _collectFrom(roles, authLike); // harvest roles from ALL known places
  return roles; // the final normalized set
}

/**
 * Public: check if the provided auth/user has at least one of the required roles.
 * - required may be a single string ("admin") or an array (["admin","auditor"])
 */
export function hasRole(authLike, required) {
  const roles = deriveRoles(authLike); // normalize roles first
  if (Array.isArray(required)) {
    // true if any of the required roles exist in normalized set
    return required.some((r) => roles.has((r ?? "").toString().trim()));
  }
  // single string form
  return roles.has((required ?? "").toString().trim());
}
