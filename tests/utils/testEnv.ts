export const E2E_BASE_URL   = process.env.E2E_BASE_URL   || 'https://Tenantra.homsi-co.com';
export const E2E_ADMIN_USER = process.env.E2E_ADMIN_USER || '';
export const E2E_ADMIN_PASS = process.env.E2E_ADMIN_PASS || '';
export const E2E_STD_USER   = process.env.E2E_STD_USER   || '';
export const E2E_STD_PASS   = process.env.E2E_STD_PASS   || '';
if (!E2E_BASE_URL) throw new Error('E2E_BASE_URL missing');
