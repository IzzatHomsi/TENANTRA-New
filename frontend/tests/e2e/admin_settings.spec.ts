import { test, expect } from '@playwright/test';

const BASE = process.env.FRONTEND_BASE || 'http://localhost:5173';
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || 'Admin@1234';

test.describe('Admin Settings smoke', () => {
  test('loads without extension banner and surfaces module load failures', async ({ page }) => {
    await page.route('**/api/admin/modules', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'forced failure for test' }),
      });
    });

    await page.goto(`${BASE}/login`);
    await page.getByPlaceholder('Username').fill(ADMIN_USER);
    await page.getByPlaceholder('Password').fill(ADMIN_PASS);
    await page.getByRole('button', { name: 'Login' }).click();
    await page.waitForURL('**/app/**');

    await page.goto(`${BASE}/app/admin-settings`);

    await expect(page.getByRole('heading', { name: 'Admin Settings' })).toBeVisible();
    await expect(page.locator('text="Browser extensions detected."')).toHaveCount(0);

    await page.getByRole('button', { name: 'Modules' }).click();
    await expect(page.locator('text=Unable to load modules right now.')).toBeVisible();
  });

  test('allows switching themes from the shell settings menu', async ({ page }) => {
    await page.goto(`${BASE}/login`);
    await page.getByPlaceholder('Username').fill(ADMIN_USER);
    await page.getByPlaceholder('Password').fill(ADMIN_PASS);
    await page.getByRole('button', { name: 'Login' }).click();
    await page.waitForURL('**/app/**');

    // Open shell settings menu (gear icon)
    await page.getByRole('button', { name: 'System settings' }).click();

    const select = page.getByLabel('Theme');
    await select.selectOption('dark');
    await expect.poll(async () => page.evaluate(() => document.documentElement.classList.contains('dark'))).toBeTruthy();

    await select.selectOption('light');
    await expect.poll(async () => page.evaluate(() => document.documentElement.classList.contains('dark'))).toBeFalsy();

    const swActive = await page.evaluate(async () => {
      if (!('serviceWorker' in navigator)) return false;
      try {
        const registration = await navigator.serviceWorker.ready;
        return Boolean(registration && registration.active);
      } catch {
        return false;
      }
    });
    await expect(swActive).toBeTruthy();
  });
});
