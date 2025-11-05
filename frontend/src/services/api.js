import { getApiBase } from "../utils/apiBase";
// Central API helpers
const BASE = getApiBase();

function okOrThrow(res) {
  if (res.ok) return res;
  return res.json().catch(()=>({})).then(j=>{
    const detail = j?.detail ? JSON.stringify(j.detail) : '';
    throw new Error(`HTTP ${res.status} ${res.statusText} ${detail}`);
  });
}

export async function login(username, password) {
  const body = new URLSearchParams();
  body.set('username', username);
  body.set('password', password);

  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
    },
    body,
  }).then(okOrThrow);

  return res.json();
}

export async function authMe(token) {
  const res = await fetch(`${BASE}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` },
  }).then(okOrThrow);
  return res.json();
}

