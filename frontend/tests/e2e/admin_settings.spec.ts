import { test, expect } from '@playwright/test';
import { APP_BASE, loginAsAdmin, stubAdminSettingsApis } from './testEnv';

test.beforeEach(async ({ page }) => {
  await stubAdminSettingsApis(page);
});

test.describe('Admin Settings smoke', () => {
  test('loads without extension banner and surfaces module load failures', async ({ page }) => {
    await page.route('**/api/admin/modules', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'forced failure for test' }),
      });
    });

    await loginAsAdmin(page);
    await page.goto(`${APP_BASE}/admin-settings`);

    await expect(page.getByRole('heading', { name: 'Admin Settings' })).toBeVisible();
    await expect(page.locator('text="Browser extensions detected."')).toHaveCount(0);

    await page.getByRole('button', { name: 'Modules' }).click();
    await expect(page.locator('text=Unable to load modules right now.')).toBeVisible();
  });

  test('allows switching themes from the shell settings menu', async ({ page }) => {
    await loginAsAdmin(page);

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
