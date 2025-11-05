import React, { useEffect, useState, useCallback } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import Modal from "../components/ui/Modal.jsx";
import UserForm from "../components/UserForm.jsx";
import { useUIStore } from "../store/uiStore";
import { fetchTenants } from "../api/tenants";

const ADMIN_ROLES = ["admin", "administrator", "super_admin", "system_admin"];
const SUPER_ADMIN_ROLES = ["super_admin", "system_admin"];
const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
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

export default function Users() {
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
    const map = new Map();
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
        body: JSON.stringify(payload),
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
          headers: authHeaders(token),
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
    return (
      <div className="bg-neutral flex h-full items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Access Denied</h1>
          <p className="mt-4 text-lg">You do not have permission to view this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <Button onClick={() => {
          setSelectedUser(null);
          setIsModalOpen(true);
        }}>Create User</Button>
      </header>

      {error && (
        <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">
          {error}
        </div>
      )}

      <Card className="p-0">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Username</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Role</th>
                {isSuperAdmin && (
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Tenant</th>
                )}
                <th className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {loading ? (
                <tr>
                  <td colSpan={isSuperAdmin ? 5 : 4} className="py-12 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={isSuperAdmin ? 5 : 4} className="py-12 text-center text-gray-500">
                    No users found.
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id}>
                    <td className="whitespace-nowrap px-6 py-4">{user.username}</td>
                    <td className="whitespace-nowrap px-6 py-4">{user.email}</td>
                    <td className="whitespace-nowrap px-6 py-4">{user.role}</td>
                    {isSuperAdmin && (
                      <td className="whitespace-nowrap px-6 py-4">
                        {tenantLookup.get(user.tenant_id) || user.tenant_id || "-"}
                      </td>
                    )}
                    <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                      <Button
                        variant="ghost"
                        onClick={() => {
                          setSelectedUser(user);
                          setIsModalOpen(true);
                        }}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        className="ml-4 text-red-600 hover:text-red-900"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {isModalOpen && (
        <Modal onClose={() => setIsModalOpen(false)}>
          <UserForm
            user={selectedUser}
            onSave={handleSaveUser}
            onCancel={() => setIsModalOpen(false)}
            tenants={tenants}
            canChooseTenant={isSuperAdmin}
            tenantsLoading={tenantsLoading}
          />
        </Modal>
      )}
    </div>
  );
}
