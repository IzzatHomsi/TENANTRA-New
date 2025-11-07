import { test, expect } from '@playwright/test';
import { APP_BASE, loginAsAdmin } from './testEnv';

async function login(page) {
  await loginAsAdmin(page);
}

test.describe('Notifications surfaces', () => {
  test('notifications list renders remote data', async ({ page }) => {
    await login(page);
    await page.goto(`${APP_BASE}/dashboard`);

    await page.route('**/api/notifications', async (route) => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, title: 'Agent Offline', message: 'agent-1 disconnected', sent_at: '2024-01-05T12:00:00Z' },
          { id: 2, title: 'Scan Failed', message: 'weekly baseline', sent_at: '2024-01-05T14:30:00Z' },
        ]),
      });
    });

    await page.goto(`${APP_BASE}/notifications`);
    await expect(page.getByRole('heading', { name: 'Notifications' })).toBeVisible();
    await expect(page.getByText('Agent Offline')).toBeVisible();
    await expect(page.getByText('weekly baseline')).toBeVisible();
  });

  test('notification history applies filters to request', async ({ page }) => {
    await login(page);

    const captured: string[] = [];
    await page.route('**/api/notification-history**', async (route) => {
      captured.push(route.request().url());
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify([
          { sent_at: '2024-01-01T09:00:00Z', channel: 'email', recipient: 'ops@example.com', subject: 'Weekly digest', status: 'sent' },
        ]),
      });
    });

    await page.goto(`${APP_BASE}/notification-history`);
    await expect(page.getByRole('heading', { name: 'Notification History' })).toBeVisible();

    await page.getByPlaceholder('Channel (email, sms, webhook)').fill('email');
    await page.getByPlaceholder('Recipient').fill('ops@example.com');
    await page.getByRole('combobox').selectOption('100');
    await page.getByRole('button', { name: 'Apply' }).click();

    await expect.poll(() => captured.length).toBeGreaterThan(0);
    const lastUrl = captured[captured.length - 1];
    const decodedUrl = decodeURIComponent(lastUrl);
    expect(decodedUrl).toContain('channel=email');
    expect(decodedUrl).toContain('recipient=ops@example.com');
    expect(decodedUrl).toContain('limit=100');
    await expect(page.getByText('Weekly digest')).toBeVisible();
  });

  test('alert settings persist channel toggles', async ({ page }) => {
    await page.route('**/api/notification-prefs', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          contentType: 'application/json',
          body: JSON.stringify({
            channels: { email: true, webhook: false },
            events: { scan_failed: true, compliance_violation: true, agent_offline: false, threshold_breach: false },
            digest: 'hourly',
          }),
        });
      } else {
        const body = await route.request().postDataJSON();
        expect(body.channels.webhook).toBe(true);
        expect(body.events.agent_offline).toBe(true);
        await route.fulfill({
          contentType: 'application/json',
          body: JSON.stringify(body),
        });
      }
    });

    await login(page);

    await page.goto(`${APP_BASE}/alert-settings`);
    await expect(page.getByRole('heading', { name: 'Alert Settings' })).toBeVisible();

    await page.getByLabel('Webhook').check();
    await page.getByLabel('Agent Offline').check();
    await page.getByRole('button', { name: 'Save Preferences' }).click();
    await expect(page.getByRole('button', { name: 'Save Preferences' })).toBeEnabled();
  });
});
