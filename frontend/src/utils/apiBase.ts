export function getApiBase(): string {
  const raw = (import.meta.env.VITE_API_URL ?? import.meta.env.VITE_API_BASE ?? '/api').toString().trim();
  if (/^https?:\/\//i.test(raw)) {
    return raw.replace(/\/+$/, '');
  }
  const path = raw.startsWith('/') ? raw : `/${raw}`;
  if (typeof window !== 'undefined' && window.location?.origin) {
    return `${window.location.origin}${path}`.replace(/\/+$/, '');
  }
  return path.replace(/\/+$/, '') || '/api';
}
