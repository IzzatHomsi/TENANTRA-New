import { jsx, jsxs } from "react/jsx-runtime";
import React, { useState, useCallback, useEffect } from "react";
import { u as useAuth, g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import { u as useUIStore } from "./apiClient-Y8eZ7muQ.js";
import { f as fetchTenants } from "./tenants-Cz2KWSMQ.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
import "zustand";
import "zustand/middleware";
import "zod";
function Modal({ children, onClose }) {
  return /* @__PURE__ */ jsx("div", { className: "fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50", children: /* @__PURE__ */ jsxs("div", { className: "relative w-full max-w-lg rounded-lg bg-white p-8 shadow-lg", children: [
    /* @__PURE__ */ jsx(
      "button",
      {
        className: "absolute top-4 right-4 text-gray-500 hover:text-gray-700",
        onClick: onClose,
        children: "×"
      }
    ),
    children
  ] }) });
}
const defaultFormState = (opts) => {
  const { user, canChooseTenant, tenants } = opts;
  const initialTenant = (() => {
    if (!canChooseTenant) return null;
    if (user?.tenant_id !== void 0 && user?.tenant_id !== null) {
      return String(user.tenant_id);
    }
    if (tenants && tenants.length > 0) {
      return String(tenants[0].id);
    }
    return "";
  })();
  return {
    id: user?.id ?? null,
    username: user?.username ?? "",
    email: user?.email ?? "",
    password: "",
    role: user?.role ?? "standard_user",
    tenant_id: initialTenant
  };
};
function UserForm({
  user,
  tenants = [],
  canChooseTenant = false,
  tenantsLoading = false,
  onSave,
  onCancel
}) {
  const [formData, setFormData] = React.useState(
    () => defaultFormState({ user, canChooseTenant, tenants })
  );
  React.useEffect(() => {
    setFormData(defaultFormState({ user, canChooseTenant, tenants }));
  }, [user, tenants, canChooseTenant]);
  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };
  const handleSubmit = (event) => {
    event.preventDefault();
    onSave(formData);
  };
  return /* @__PURE__ */ jsxs("form", { onSubmit: handleSubmit, className: "space-y-6", children: [
    /* @__PURE__ */ jsx("h2", { className: "text-2xl font-bold", children: user ? "Edit User" : "Create User" }),
    !user && /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Username" }),
      /* @__PURE__ */ jsx(
        "input",
        {
          type: "text",
          name: "username",
          value: formData.username,
          onChange: handleChange,
          className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          required: true
        }
      )
    ] }),
    /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Email" }),
      /* @__PURE__ */ jsx(
        "input",
        {
          type: "email",
          name: "email",
          value: formData.email,
          onChange: handleChange,
          className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          required: true
        }
      )
    ] }),
    /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Password" }),
      /* @__PURE__ */ jsx(
        "input",
        {
          type: "password",
          name: "password",
          value: formData.password,
          onChange: handleChange,
          className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          placeholder: user ? "Leave blank to keep current password" : ""
        }
      )
    ] }),
    /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Role" }),
      /* @__PURE__ */ jsxs(
        "select",
        {
          name: "role",
          value: formData.role,
          onChange: handleChange,
          className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "standard_user", children: "Standard User" }),
            /* @__PURE__ */ jsx("option", { value: "admin", children: "Admin" })
          ]
        }
      )
    ] }),
    canChooseTenant && /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Tenant" }),
      /* @__PURE__ */ jsxs(
        "select",
        {
          name: "tenant_id",
          value: formData.tenant_id ?? "",
          onChange: handleChange,
          className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          required: true,
          disabled: tenantsLoading,
          children: [
            /* @__PURE__ */ jsx("option", { value: "", children: tenantsLoading ? "Loading..." : "Select tenant" }),
            tenants.map((tenant) => /* @__PURE__ */ jsx("option", { value: String(tenant.id), children: tenant.name || tenant.slug || `Tenant ${tenant.id}` }, tenant.id))
          ]
        }
      )
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "flex justify-end space-x-4", children: [
      /* @__PURE__ */ jsx(Button, { type: "button", variant: "ghost", onClick: onCancel, children: "Cancel" }),
      /* @__PURE__ */ jsx(Button, { type: "submit", children: "Save" })
    ] })
  ] });
}
const ADMIN_ROLES = ["admin", "administrator", "super_admin", "system_admin"];
const SUPER_ADMIN_ROLES = ["super_admin", "system_admin"];
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
const isStrongPassword = (pw) => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(pw);
const readErr = async (res) => {
  try {
    const text = await res.text();
    try {
      const json = JSON.parse(text);
      return json?.detail || json?.message || text;
    } catch {
      return text;
    }
  } catch {
    return `HTTP ${res.status}`;
  }
};
function Users() {
  const { role, token, signOut } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [tenantsLoading, setTenantsLoading] = useState(false);
  const { tenants, setTenants } = useUIStore();
  const isAdmin = React.useMemo(() => ADMIN_ROLES.includes(role || ""), [role]);
  const isSuperAdmin = React.useMemo(() => SUPER_ADMIN_ROLES.includes(role || ""), [role]);
  const tenantLookup = React.useMemo(() => {
    const map = /* @__PURE__ */ new Map();
    tenants.forEach((tenant) => {
      map.set(tenant.id, tenant.name || tenant.slug || `Tenant ${tenant.id}`);
    });
    return map;
  }, [tenants]);
  const refreshUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/users`, { headers: authHeaders(token) });
      if (res.status === 401) {
        signOut?.();
        return;
      }
      if (!res.ok) {
        const msg = await readErr(res);
        throw new Error(msg || `Failed to load users (HTTP ${res.status})`);
      }
      const data = await res.json();
      setUsers(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e.message || "Failed to load users.");
    } finally {
      setLoading(false);
    }
  }, [token, signOut]);
  const refreshTenants = useCallback(async () => {
    if (!isSuperAdmin) {
      setTenants([]);
      return;
    }
    setTenantsLoading(true);
    try {
      await fetchTenants(token);
    } catch (e) {
      setError(e.message || "Failed to load tenants.");
    } finally {
      setTenantsLoading(false);
    }
  }, [isSuperAdmin, token, signOut]);
  useEffect(() => {
    if (isAdmin) {
      refreshUsers();
    }
  }, [isAdmin, refreshUsers]);
  useEffect(() => {
    if (isSuperAdmin) {
      refreshTenants();
    }
  }, [isSuperAdmin, refreshTenants]);
  const handleSaveUser = async (formData) => {
    setError("");
    const isCreating = !formData.id;
    if (isCreating) {
      if (!formData.username.trim()) return setError("Username is required.");
      if (!formData.email.trim() || !/\S+@\S+\.\S+/.test(formData.email)) {
        return setError("Valid email is required.");
      }
      if (!isStrongPassword(formData.password)) {
        return setError("Password must be at least 8 chars and include upper, lower, digit, and special char.");
      }
    } else {
      if (formData.password && !isStrongPassword(formData.password)) {
        return setError("Password must be at least 8 chars and include upper, lower, digit, and special char.");
      }
    }
    const url = isCreating ? `${API_BASE}/users` : `${API_BASE}/users/${formData.id}`;
    const method = isCreating ? "POST" : "PUT";
    const payload = { ...formData };
    if (isCreating) {
      delete payload.id;
    }
    if (isSuperAdmin) {
      if (!payload.tenant_id) {
        return setError("Tenant selection is required for this action.");
      }
      payload.tenant_id = Number(payload.tenant_id);
    } else {
      delete payload.tenant_id;
    }
    if (!payload.password) {
      delete payload.password;
    }
    if (!isCreating) {
      delete payload.username;
    }
    try {
      const res = await fetch(url, {
        method,
        headers: authHeaders(token),
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const msg = await readErr(res);
        throw new Error(msg || `Failed to save user (HTTP ${res.status})`);
      }
      setIsModalOpen(false);
      await refreshUsers();
    } catch (e) {
      setError(e.message || "Failed to save user.");
    }
  };
  const handleDeleteUser = async (userId) => {
    setError("");
    if (window.confirm("Are you sure you want to delete this user?")) {
      try {
        const res = await fetch(`${API_BASE}/users/${userId}`, {
          method: "DELETE",
          headers: authHeaders(token)
        });
        if (!res.ok) {
          const msg = await readErr(res);
          throw new Error(msg || `Delete failed (HTTP ${res.status})`);
        }
        await refreshUsers();
      } catch (e) {
        setError(e.message || "Failed to delete user.");
      }
    }
  };
  if (!isAdmin) {
    return /* @__PURE__ */ jsx("div", { className: "bg-facebook-gray flex h-full items-center justify-center", children: /* @__PURE__ */ jsxs("div", { className: "text-center", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold", children: "Access Denied" }),
      /* @__PURE__ */ jsx("p", { className: "mt-4 text-lg", children: "You do not have permission to view this page." })
    ] }) });
  }
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8 flex items-center justify-between", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "User Management" }),
      /* @__PURE__ */ jsx(Button, { onClick: () => {
        setSelectedUser(null);
        setIsModalOpen(true);
      }, children: "Create User" })
    ] }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsx(Card, { className: "p-0", children: /* @__PURE__ */ jsx("div", { className: "overflow-x-auto", children: /* @__PURE__ */ jsxs("table", { className: "min-w-full divide-y divide-gray-200", children: [
      /* @__PURE__ */ jsx("thead", { className: "bg-gray-50", children: /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Username" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Email" }),
        /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Role" }),
        isSuperAdmin && /* @__PURE__ */ jsx("th", { className: "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500", children: "Tenant" }),
        /* @__PURE__ */ jsx("th", { className: "relative px-6 py-3", children: /* @__PURE__ */ jsx("span", { className: "sr-only", children: "Actions" }) })
      ] }) }),
      /* @__PURE__ */ jsx("tbody", { className: "divide-y divide-gray-200 bg-white", children: loading ? /* @__PURE__ */ jsx("tr", { children: /* @__PURE__ */ jsx("td", { colSpan: isSuperAdmin ? 5 : 4, className: "py-12 text-center text-gray-500", children: "Loading..." }) }) : users.length === 0 ? /* @__PURE__ */ jsx("tr", { children: /* @__PURE__ */ jsx("td", { colSpan: isSuperAdmin ? 5 : 4, className: "py-12 text-center text-gray-500", children: "No users found." }) }) : users.map((user) => /* @__PURE__ */ jsxs("tr", { children: [
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: user.username }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: user.email }),
        /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: user.role }),
        isSuperAdmin && /* @__PURE__ */ jsx("td", { className: "whitespace-nowrap px-6 py-4", children: tenantLookup.get(user.tenant_id) || user.tenant_id || "-" }),
        /* @__PURE__ */ jsxs("td", { className: "whitespace-nowrap px-6 py-4 text-right text-sm font-medium", children: [
          /* @__PURE__ */ jsx(
            Button,
            {
              variant: "ghost",
              onClick: () => {
                setSelectedUser(user);
                setIsModalOpen(true);
              },
              children: "Edit"
            }
          ),
          /* @__PURE__ */ jsx(
            Button,
            {
              variant: "ghost",
              className: "ml-4 text-red-600 hover:text-red-900",
              onClick: () => handleDeleteUser(user.id),
              children: "Delete"
            }
          )
        ] })
      ] }, user.id)) })
    ] }) }) }),
    isModalOpen && /* @__PURE__ */ jsx(Modal, { onClose: () => setIsModalOpen(false), children: /* @__PURE__ */ jsx(
      UserForm,
      {
        user: selectedUser,
        onSave: handleSaveUser,
        onCancel: () => setIsModalOpen(false),
        tenants,
        canChooseTenant: isSuperAdmin,
        tenantsLoading
      }
    ) })
  ] });
}
export {
  Users as default
};
