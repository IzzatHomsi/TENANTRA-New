import axios from "axios";
import { getApiBase } from "../utils/apiBase";

const client = axios.create({ baseURL: getApiBase() });

export const getComplianceTrends = async (days = 30, module) => {
  const token = localStorage.getItem("token");
  if (!token) return [];
  const params = { days };
  if (module) params.module = module;
  const res = await client.get("/compliance/trends", {
    headers: { Authorization: `Bearer ${token}` },
    params,
  });
  return res.data;
};
