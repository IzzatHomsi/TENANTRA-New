import { getApiBase } from "./utils/apiBase";
import axios, { AxiosError, AxiosHeaders } from "axios";
import type { AxiosRequestHeaders } from "axios";

const API_BASE = getApiBase();

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 20000,
  withCredentials: false,
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
});

function getToken() {
  try {
    return localStorage.getItem('token');
  } catch {
    return null;
  }
}

export function setToken(t: string | null) {
  try {
    if (t) {
      localStorage.setItem('token', t);
    } else {
      localStorage.removeItem('token');
    }
  } catch {}
}

api.interceptors.request.use((cfg) => {
  const t = getToken();
  if (!t) return cfg;

  if (cfg.headers instanceof AxiosHeaders) {
    cfg.headers.set("Authorization", `Bearer ${t}`);
  } else if (cfg.headers) {
    (cfg.headers as AxiosRequestHeaders)["Authorization"] = `Bearer ${t}`;
  } else {
    cfg.headers = new AxiosHeaders({ Authorization: `Bearer ${t}` });
  }
  return cfg;
});

api.interceptors.response.use(
  r => r,
  (e: AxiosError) => {
    if (e.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timed out.'));
    }
    if (e.response) {
      try {
        const status = e.response.status || 0;
        const detail = (e.response.data as any)?.detail ?? `HTTP ${status}`;
        if (status === 401) {
          try { window.dispatchEvent(new CustomEvent('tena:auth-error', { detail: { status, message: String(detail) } })); } catch {}
        } else if (status === 403) {
          try { window.dispatchEvent(new CustomEvent('tena:notice', { detail: { type: 'warn', message: 'Access denied.' } })); } catch {}
        }
        return Promise.reject(new Error(String(detail)));
      } catch {
        return Promise.reject(new Error(`HTTP ${e.response.status}`));
      }
    }
    return Promise.reject(new Error('Network error.'));
  }
);

export async function login(username: string, password: string) {
  const form = new URLSearchParams();
  form.set('username', username);
  form.set('password', password);
  const res = await api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
  const tk = (res.data as any)?.access_token;
  if (tk) setToken(tk);
  return res.data;
}

export async function me() {
  const res = await api.get('/auth/me');
  return res.data;
}
