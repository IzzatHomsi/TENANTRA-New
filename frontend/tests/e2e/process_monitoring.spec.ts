import { test, expect } from '@playwright/test';

const BASE = process.env.FRONTEND_BASE || 'http://localhost:5173';
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || 'Admin@1234';

test('Process Monitoring page renders after login', async ({ page }) => {
  await page.goto(`${BASE}/login`);
  await page.getByPlaceholder('Username').fill(ADMIN_USER);
  await page.getByPlaceholder('Password').fill(ADMIN_PASS);
  await page.getByRole('button', { name: 'Login' }).click();
  await page.waitForURL('**/app/**');

  await page.goto(`${BASE}/app/process-monitoring`);
  await expect(page.getByRole('heading', { name: 'Process Monitoring & Drift' })).toBeVisible();
  await expect(page.getByText('Drift Events')).toBeVisible();
  await expect(page.getByText('Baseline')).toBeVisible();
});

test('Tenant baseline can be saved from UI', async ({ page }) => {
  await page.goto(`${BASE}/login`);
  await page.getByPlaceholder('Username').fill(ADMIN_USER);
  await page.getByPlaceholder('Password').fill(ADMIN_PASS);
  await page.getByRole('button', { name: 'Login' }).click();
  await page.waitForURL('**/app/**');

  await page.goto(`${BASE}/app/process-monitoring`);

  // Set scope to tenant default baseline (no agent required)
  await page.getByLabel('Scope').selectOption('tenant');

  // Add a minimal entry and save
  await page.getByRole('button', { name: 'Add entry' }).click();
  const nameInput = page.getByPlaceholder('process.exe').first();
  await nameInput.fill('example.exe');
  await page.getByRole('button', { name: 'Save baseline' }).click();

  // Expect success message
  await expect(page.getByText('Baseline updated successfully.')).toBeVisible();
});
