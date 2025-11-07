import { test, expect } from '@playwright/test';
import { APP_BASE, loginAsAdmin, stubProcessMonitoringApis } from './testEnv';

test.beforeEach(async ({ page }) => {
  await stubProcessMonitoringApis(page);
});

test('Process Monitoring page renders after login', async ({ page }) => {
  await loginAsAdmin(page);
  await page.goto(`${APP_BASE}/process-monitoring`);
  await expect(page.getByRole('heading', { name: 'Process Monitoring & Drift' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Drift Events' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Agent Baseline' })).toBeVisible();
});

test('Tenant baseline can be saved from UI', async ({ page }) => {
  await loginAsAdmin(page);

  await page.goto(`${APP_BASE}/process-monitoring`);
  await expect(page.getByRole('heading', { name: 'Process Monitoring & Drift' })).toBeVisible();

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
