import { test, expect } from '@playwright/test';

const BASE = process.env.FRONTEND_BASE || 'http://localhost:5173';
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || 'Admin@1234';

test('Integrity page: save ignores and baselines, use filters and diff', async ({ page }) => {
  await page.goto(`${BASE}/login`);
  await page.getByPlaceholder('Username').fill(ADMIN_USER);
  await page.getByPlaceholder('Password').fill(ADMIN_PASS);
  await page.getByRole('button', { name: 'Login' }).click();
  await page.waitForURL('**/app/**');

  await page.goto(`${BASE}/app/integrity`);
  await expect(page.getByText('Services')).toBeVisible();

  // Save registry ignores
  const regIg = page.getByPlaceholder('SOFTWARE\\...');
  await regIg.fill('SOFTWARE\\Microsoft');
  await page.getByRole('button', { name: 'Save Ignores' }).click();

  // Add a service baseline row and save (tenant scope)
  await page.getByRole('button', { name: 'Add' }).first().click(); // first baseline editor is services
  const svcName = page.locator('table').nth(2).getByRole('textbox').first();
  await svcName.fill('svc-test');
  await page.getByRole('button', { name: 'Save' }).first().click();

  // Filters for events
  await page.getByLabel('Type').fill('service_change');
  await page.getByLabel('Severity').selectOption('high');
  await page.getByRole('button', { name: 'Load' }).click();

  // Diff controls (no agent/timestamps yet, ensure UI elements work)
  await page.getByLabel('Left').fill('2025-01-01T00:00');
  await page.getByLabel('Right').fill('2025-01-01T01:00');
  await page.getByRole('button', { name: 'Diff' }).click();

  // Expect diff result panels present
  await expect(page.getByText('Service changes')).toBeVisible();
  await expect(page.getByText('Registry changes')).toBeVisible();
});

test('Agent-level ignores and agent baseline save', async ({ page }) => {
  await page.goto(`${BASE}/login`);
  await page.getByPlaceholder('Username').fill(ADMIN_USER);
  await page.getByPlaceholder('Password').fill(ADMIN_PASS);
  await page.getByRole('button', { name: 'Login' }).click();
  await page.waitForURL('**/app/**');

  await page.goto(`${BASE}/app/integrity`);
  await page.getByLabel('Scope').selectOption('agent');
  await page.getByLabel('Agent ID').fill('1');

  // Save agent-level service ignores
  const agentIg = page.locator('#svcIgAgent');
  await agentIg.fill('svcX,svcY');
  await page.getByRole('button', { name: 'Save Agent Ignores' }).click();

  // Save an agent-scoped service baseline row
  await page.getByRole('button', { name: 'Add' }).first().click();
  const nameInput = page.locator('table').nth(2).getByRole('textbox').first();
  await nameInput.fill('svc-agent-1');
  await page.getByRole('button', { name: 'Save' }).first().click();
});
