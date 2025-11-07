import { test, expect } from '@playwright/test';
import { APP_BASE, loginAsAdmin, stubIntegrityApis } from './testEnv';

test.beforeEach(async ({ page }) => {
  await stubIntegrityApis(page);
});

test('Integrity page: save ignores and baselines, use filters and diff', async ({ page }) => {
  await loginAsAdmin(page);

  await page.goto(`${APP_BASE}/integrity`);
  await expect(page.getByTestId('integrity-services-heading')).toBeVisible();

  // Save registry ignores
  const regIg = page.getByLabel('Registry Ignores');
  await regIg.fill('SOFTWARE\\Microsoft');
  await page.getByRole('button', { name: 'Save Ignores' }).click();

  // Add a service baseline row and save (tenant scope)
  const serviceSection = page.getByTestId('service-baseline-section');
  await expect(serviceSection).toBeVisible();
  const addButton = serviceSection.getByRole('button', { name: 'Add' });
  await expect(addButton).toBeVisible();
  await addButton.click();
  const svcName = serviceSection.getByTestId('service-baseline-table').getByRole('textbox').first();
  await svcName.fill('svc-test');
  await serviceSection.getByRole('button', { name: 'Save' }).click();

  // Filters for events
  await page.getByLabel('Type').fill('service_change');
  await page.getByLabel('Severity').selectOption('high');
  await page.getByRole('button', { name: 'Load' }).click();

  // Diff controls (ensure agent context so button is enabled)
  await page.getByLabel('Scope').selectOption('agent');
  await page.getByLabel('Agent ID').fill('1');
  await page.getByLabel('Left').fill('2025-01-01T00:00');
  await page.getByLabel('Right').fill('2025-01-01T01:00');
  await page.getByRole('button', { name: 'Diff' }).click();

  // Expect diff result panels present
  await expect(page.getByText('Service changes')).toBeVisible();
  await expect(page.getByText('Registry changes')).toBeVisible();
});

test('Agent-level ignores and agent baseline save', async ({ page }) => {
  await loginAsAdmin(page);

  await page.goto(`${APP_BASE}/integrity`);
  await page.getByLabel('Scope').selectOption('agent');
  await page.getByLabel('Agent ID').fill('1');

  // Save agent-level service ignores
  const agentIg = page.getByLabel('Service Ignores');
  await agentIg.fill('svcX,svcY');
  await page.getByRole('button', { name: 'Save Agent Ignores' }).click();

  // Save an agent-scoped service baseline row
  const serviceSection = page.getByTestId('service-baseline-section');
  await expect(serviceSection).toBeVisible();
  const addButton = serviceSection.getByRole('button', { name: 'Add' });
  await expect(addButton).toBeVisible();
  await addButton.click();
  const nameInput = serviceSection.getByTestId('service-baseline-table').getByRole('textbox').first();
  await nameInput.fill('svc-agent-1');
  await serviceSection.getByRole('button', { name: 'Save' }).click();
});
