import axios from "axios";
import { getApiBase } from "../utils/apiBase";

const client = axios.create({ baseURL: getApiBase() });

export const getNotifications = async (status) => {
  const token = localStorage.getItem("token");
  if (!token) return [];
  const params = status ? { status } : {};
  const res = await client.get("/notifications/me", {
    headers: { Authorization: `Bearer ${token}` },
    params,
  });
  return res.data;
};

export const markNotificationRead = async (id) => {
  const token = localStorage.getItem("token");
  if (!token) return;
  const res = await client.post(`/notifications/${id}/read`, null, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};
