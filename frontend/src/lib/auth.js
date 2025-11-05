function b64decodeUnicode(str) {
  try {
    return decodeURIComponent(
      atob(str.replace(/-/g, '+').replace(/_/g, '/'))
        .split('')
        .map(function(c) { return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2); })
        .join('')
    );
  } catch (e) {
    return null;
  }
}
function parseJwtExp(token) {
  if (!token || token.split('.').length < 2) return null;
  try {
    const payload = token.split('.')[1];
    const json = b64decodeUnicode(payload);
    if (!json) return null;
    const data = JSON.parse(json);
    if (data && typeof data.exp === 'number') {
      return data.exp * 1000;
    }
  } catch (_e) {}
  return null;
}
export function saveAuth(token, user, expiresInSeconds) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user || null));
  let expMs = null;
  if (typeof expiresInSeconds === 'number' && isFinite(expiresInSeconds)) {
    expMs = Date.now() + (expiresInSeconds * 1000);
  } else {
    expMs = parseJwtExp(token);
  }
  if (expMs) {
    localStorage.setItem('token_exp', String(expMs));
  } else {
    localStorage.removeItem('token_exp');
  }
}
export function getToken() { return localStorage.getItem('token'); }
export function getUser() {
  try { const raw = localStorage.getItem('user'); return raw ? JSON.parse(raw) : null; }
  catch (_e) { return null; }
}
export function clearAuth() {
  localStorage.removeItem('token'); localStorage.removeItem('user'); localStorage.removeItem('token_exp');
}
export function isAuthenticated() {
  const token = getToken();
  if (!token) return false;
  const exp = Number(localStorage.getItem('token_exp') || 0);
  if (exp && Date.now() > exp) { clearAuth(); return false; }
  return true;
}
