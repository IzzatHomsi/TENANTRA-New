import { test, expect } from '@playwright/test';

const BASE = process.env.FRONTEND_BASE || 'http://localhost:5173';
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || 'Admin@1234';

async function login(page) {
  await page.goto(`${BASE}/login`);
  await page.getByPlaceholder('Username').fill(ADMIN_USER);
  await page.getByPlaceholder('Password').fill(ADMIN_PASS);
  await page.getByRole('button', { name: 'Login' }).click();
  await page.waitForURL('**/app/**');
}

test.describe('Notifications surfaces', () => {
  test('notifications list renders remote data', async ({ page }) => {
    await login(page);

    await page.route('**/api/notifications', async (route) => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, title: 'Agent Offline', message: 'agent-1 disconnected', sent_at: '2024-01-05T12:00:00Z' },
          { id: 2, title: 'Scan Failed', message: 'weekly baseline', sent_at: '2024-01-05T14:30:00Z' },
        ]),
      });
    });

    await page.goto(`${BASE}/app/notifications`);
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
        body: JSON.stringify({
          items: [
            { sent_at: '2024-01-01T09:00:00Z', channel: 'email', recipient: 'ops@example.com', subject: 'Weekly digest', status: 'sent' },
          ],
          total: 1,
        }),
      });
    });

    await page.goto(`${BASE}/app/notification-history`);
    await expect(page.getByRole('heading', { name: 'Notification History' })).toBeVisible();

    await page.getByPlaceholder('Channel (email, sms, webhook)').fill('email');
    await page.getByPlaceholder('Recipient').fill('ops@example.com');
    await page.getByRole('combobox').selectOption('100');
    await page.getByRole('button', { name: 'Apply' }).click();

    await expect.poll(() => captured.length).toBeGreaterThan(0);
    const lastUrl = captured[captured.length - 1];
    expect(lastUrl).toContain('channel=email');
    expect(lastUrl).toContain('recipient=ops@example.com');
    expect(lastUrl).toContain('limit=100');
    await expect(page.getByText('Weekly digest')).toBeVisible();
  });

  test('alert settings persist channel toggles', async ({ page }) => {
    await login(page);

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

    await page.goto(`${BASE}/app/alert-settings`);
    await expect(page.getByRole('heading', { name: 'Alert Settings' })).toBeVisible();

    await page.getByLabel('Webhook').check();
    await page.getByLabel('Agent Offline').check();
    await page.getByRole('button', { name: 'Save Preferences' }).click();
    await expect(page.getByRole('button', { name: 'Save Preferences' })).toBeEnabled();
  });
});
