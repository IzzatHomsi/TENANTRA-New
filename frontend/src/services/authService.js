import { getApiBase } from "../utils/apiBase";
import axios from "axios";

const API_URL = getApiBase();

export const login = async (username, password) => {
  // Send form data to the authentication endpoint. The server returns
  // an object containing an ``access_token`` and a ``user`` payload. We
  // persist the token under the key "token" (not "access_token") so
  // that the AuthContext and other services reference a consistent
  // storage key. Returning the full response allows callers to
  // optionally use the ``user`` portion if needed.
  const response = await axios.post(
    `${API_URL}/auth/login`,
    new URLSearchParams({ username, password })
  );
  if (response.data.access_token) {
    localStorage.setItem("token", response.data.access_token);
  }
  return response.data;
};

export const getCurrentUser = async () => {
  // Retrieve the current user's profile using the token stored in
  // localStorage. Returns null if no token is present. The backend
  // endpoint ``/users/me`` returns id, username, email, role,
  // is_active and tenant_id.
  const token = localStorage.getItem("token");
  if (!token) return null;
  const response = await axios.get(`${API_URL}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const logout = () => {
  // Remove the persisted token. Additional cleanup (such as user info)
  // is handled by AuthContext.
  localStorage.removeItem("token");
};
