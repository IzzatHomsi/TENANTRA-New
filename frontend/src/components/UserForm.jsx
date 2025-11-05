import React from "react";
import Button from "./ui/Button.jsx";

const defaultFormState = (opts) => {
  const { user, canChooseTenant, tenants } = opts;
  const initialTenant = (() => {
    if (!canChooseTenant) return null;
    if (user?.tenant_id !== undefined && user?.tenant_id !== null) {
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
    tenant_id: initialTenant,
  };
};

export default function UserForm({
  user,
  tenants = [],
  canChooseTenant = false,
  tenantsLoading = false,
  onSave,
  onCancel,
}) {
  const [formData, setFormData] = React.useState(() =>
    defaultFormState({ user, canChooseTenant, tenants })
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

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-2xl font-bold">{user ? "Edit User" : "Create User"}</h2>
      {!user && (
        <div>
          <label className="block text-sm font-medium text-gray-700">Username</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            required
          />
        </div>
      )}
      <div>
        <label className="block text-sm font-medium text-gray-700">Email</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Password</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          placeholder={user ? "Leave blank to keep current password" : ""}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Role</label>
        <select
          name="role"
          value={formData.role}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
        >
          <option value="standard_user">Standard User</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      {canChooseTenant && (
        <div>
          <label className="block text-sm font-medium text-gray-700">Tenant</label>
          <select
            name="tenant_id"
            value={formData.tenant_id ?? ""}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            required
            disabled={tenantsLoading}
          >
            <option value="">{tenantsLoading ? "Loading..." : "Select tenant"}</option>
            {tenants.map((tenant) => (
              <option key={tenant.id} value={String(tenant.id)}>
                {tenant.name || tenant.slug || `Tenant ${tenant.id}`}
              </option>
            ))}
          </select>
        </div>
      )}
      <div className="flex justify-end space-x-4">
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">Save</Button>
      </div>
    </form>
  );
}
