import axios from "axios";
import { getApiBase } from "../utils/apiBase";

const API_BASE = getApiBase();
const client = axios.create({ baseURL: API_BASE });

function authConfig() {
  const token = localStorage.getItem("token");
  return token
    ? { headers: { Authorization: `Bearer ${token}` } }
    : { headers: {} };
}

export const getAlertRules = async () => {
  const res = await client.get("/alerts/rules", authConfig());
  return res.data;
};

export const createAlertRule = async (rule) => {
  const res = await client.post("/alerts/rules", rule, authConfig());
  return res.data;
};

export const updateAlertRule = async (id, rule) => {
  const res = await client.put(`/alerts/rules/${id}`, rule, authConfig());
  return res.data;
};

export const deleteAlertRule = async (id) => {
  const res = await client.delete(`/alerts/rules/${id}`, authConfig());
  return res.data;
};

export const getNotificationSettings = async (tenantId) => {
  const config = { ...authConfig() };
  if (tenantId != null) {
    config.params = { tenant_id: tenantId };
  }
  const res = await client.get("/notification-prefs", config);
  return res.data;
};

export const updateNotificationSettings = async (settings, tenantId) => {
  const config = { ...authConfig() };
  if (tenantId != null) {
    config.params = { tenant_id: tenantId };
  }
  const res = await client.put("/notification-prefs", settings, config);
  return res.data;
};
