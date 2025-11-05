import axios from "axios";
import { getApiBase } from "../utils/apiBase";

const client = axios.create({ baseURL: getApiBase() });

function authConfig() {
  const token = localStorage.getItem("token");
  return token
    ? { headers: { Authorization: `Bearer ${token}` } }
    : { headers: {} };
}

export const getUsers = async () => {
  const res = await client.get("/users/", authConfig());
  return res.data;
};

export const createUser = async (userData) => {
  if (!userData.password || userData.password.trim() === "") {
    throw new Error("Password is required.");
  }
  const res = await client.post("/users/create", userData, authConfig());
  return res.data;
};

export const updateUser = async (id, userData) => {
  const payload = { ...userData };
  if (payload.username !== undefined) delete payload.username;
  if (payload.password === "") delete payload.password;
  const res = await client.put(`/users/${id}`, payload, authConfig());
  return res.data;
};

export const deleteUser = async (id) => {
  const res = await client.delete(`/users/${id}`, authConfig());
  return res.data;
};
