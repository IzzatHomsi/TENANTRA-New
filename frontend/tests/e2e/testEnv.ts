import type { Page, Route } from '@playwright/test';

const rawBase =
  process.env.FRONTEND_BASE ||
  process.env.PLAYWRIGHT_BASE_URL ||
  'http://127.0.0.1:4173';

const normalized = rawBase.replace(/\/+$/, '');
export const BASE = normalized;
export const APP_BASE = `${normalized}/app`;
export const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const resolvedAdminPass = process.env.ADMIN_PASS || process.env.TENANTRA_TEST_ADMIN_PASSWORD;
if (!resolvedAdminPass) {
  throw new Error('Set ADMIN_PASS or TENANTRA_TEST_ADMIN_PASSWORD before running Playwright e2e tests.');
}
export const ADMIN_PASS = resolvedAdminPass;

const rawApiBase =
  process.env.PLAYWRIGHT_API_BASE ||
  process.env.VITE_API_URL ||
  process.env.VITE_API_PROXY_TARGET ||
  'http://127.0.0.1:5000';
export const API_BASE = rawApiBase.replace(/\/+$/, '');

const AUTH_FLAG = '__tenaAuthMockApplied';

async function ensureAuthRoutes(page: Page): Promise<void> {
  const marker = page as unknown as Record<string, unknown>;
  if (marker[AUTH_FLAG]) return;
  marker[AUTH_FLAG] = true;

  await page.route('**/api/auth/login', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: 'test-token',
        token_type: 'bearer',
        user: { id: 1, username: ADMIN_USER, role: 'admin' },
      }),
    });
  });

  await page.route('**/api/auth/me', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        user: { id: 1, username: ADMIN_USER },
        role: 'admin',
      }),
    });
  });
}

const DASHBOARD_URL_PATTERN = /\/app\/(dashboard|shell|home)(\/|$|\?)/;

async function waitForDashboard(page: Page): Promise<void> {
  const deadline = Date.now() + 15000;
  let lastError: Error | undefined;
  while (Date.now() < deadline) {
    if (DASHBOARD_URL_PATTERN.test(page.url())) {
      await page.waitForLoadState('domcontentloaded').catch(() => undefined);
      return;
    }
    try {
      await page.waitForURL(DASHBOARD_URL_PATTERN, { timeout: 2000 });
      await page.waitForLoadState('domcontentloaded').catch(() => undefined);
      return;
    } catch (error) {
      lastError = error as Error;
      await seedLocalSession(page);
      await page.goto(`${APP_BASE}/dashboard`, { waitUntil: 'domcontentloaded' }).catch(() => undefined);
    }
  }
  const message = lastError?.message || 'timeout waiting for dashboard route';
  throw new Error(`Dashboard did not load after retries (last URL: ${page.url()}): ${message}`);
}

async function seedLocalSession(page: Page): Promise<void> {
  await page.evaluate(
    ({ username }) => {
      try {
        const payload = { id: 1, username, role: 'admin' };
        window.localStorage.setItem('token', `test-token-${Date.now()}`);
        window.localStorage.setItem('user', JSON.stringify(payload));
        window.localStorage.setItem('role', 'admin');
      } catch {
        // ignore storage failures; tests will surface auth issues later
      }
    },
    { username: ADMIN_USER }
  );
}

type LoginOptions = {
  disableSw?: boolean;
};

export async function loginAsAdmin(page: Page, options: LoginOptions = {}): Promise<void> {
  await ensureAuthRoutes(page);

  const { disableSw = true } = options;
  const swMode = disableSw ? "off" : "on";
  const loginUrl = `${APP_BASE}/login?sw=${swMode}`;

  await page.goto(loginUrl, { waitUntil: 'networkidle' });
  await page.getByPlaceholder('Username').fill(ADMIN_USER);
  await page.getByPlaceholder('Password').fill(ADMIN_PASS);

  await page.getByRole('button', { name: /login/i }).click();
  await page.waitForFunction(() => {
    try {
      return Boolean(window.localStorage.getItem('token'));
    } catch {
      return false;
    }
  }, { timeout: 7000 }).catch(() => undefined);
  await seedLocalSession(page);
  await page.goto(`${APP_BASE}/dashboard`, { waitUntil: 'networkidle' });
  await waitForDashboard(page);
}

export async function stubProcessMonitoringApis(page: Page): Promise<void> {
  const processes = [
    {
      id: 1,
      agent_id: 7,
      process_name: 'example.exe',
      executable_path: 'C:\\\\Program Files\\\\Example\\\\example.exe',
      username: 'SYSTEM',
      hash: 'abc123',
      collected_at: '2024-01-05T12:00:00Z',
    },
  ];
  const drift = {
    events: [
      {
        id: 44,
        process_name: 'example.exe',
        severity: 'high',
        change_type: 'hash',
        detected_at: '2024-01-05T12:05:00Z',
      },
    ],
  };
  const baselineEntries = [
    {
      process_name: 'baseline.exe',
      executable_path: 'C:\\\\baseline.exe',
      expected_hash: 'ffff',
      expected_user: 'SYSTEM',
      is_critical: true,
      notes: 'default',
    },
  ];

  await page.route('**/api/processes/drift?**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(drift),
    });
  });

  await page.route('**/api/processes/baseline?**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ entries: baselineEntries }),
    });
  });

  await page.route('**/api/processes/baseline', async (route) => {
    if (route.request().method() === 'POST') {
      try {
        const body = await route.request().postDataJSON();
        if (Array.isArray(body?.processes)) {
          baselineEntries.splice(0, baselineEntries.length, ...body.processes);
        }
      } catch {
        // ignore parse failures for tests
      }
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'ok' }),
      });
      return;
    }
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ entries: baselineEntries }),
    });
  });

  await page.route('**/api/processes?**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(processes),
    });
  });

  await page.route('**/api/processes', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(processes),
    });
  });
}

export async function stubIntegrityApis(page: Page): Promise<void> {
  const services = [
    {
      id: 1,
      name: 'svc-test',
      status: 'running',
      start_mode: 'auto',
      run_account: 'SYSTEM',
      binary_path: 'C:\\\\svc-test.exe',
      hash: 'aa11',
    },
  ];
  const registry = [
    {
      hive: 'HKLM',
      key_path: 'SOFTWARE\\\\Tenantra',
      value_name: 'Enabled',
      value_data: '1',
      value_type: 'REG_DWORD',
    },
  ];
  const tasks = [
    {
      id: 9,
      name: 'Nightly baseline',
      schedule: '0 3 * * *',
      status: 'ready',
    },
  ];
  const svcBaseline: Array<Record<string, unknown>> = [
    {
      name: 'svc-test',
      expected_status: 'running',
      expected_start_mode: 'auto',
      expected_run_account: 'SYSTEM',
    },
  ];
  const regBaseline: Array<Record<string, unknown>> = [
    {
      hive: 'HKLM',
      key_path: 'SOFTWARE\\\\Tenantra',
      value_name: 'Enabled',
      expected_value: '1',
      expected_type: 'REG_DWORD',
      is_critical: true,
      notes: 'default',
    },
  ];
  const taskBaseline: Array<Record<string, unknown>> = [
    {
      name: 'Nightly baseline',
      command: 'baseline.exe',
      expected_user: 'SYSTEM',
    },
  ];

  const tenantSettings = [
    {
      id: 'reg-ignore',
      tenant_id: 1,
      key: 'integrity.registry.ignore_prefixes',
      value: ['SOFTWARE\\\\Microsoft'],
    },
    {
      id: 'svc-ignore',
      tenant_id: 1,
      key: 'integrity.service.ignore_names',
      value: ['svc-test'],
    },
  ];

  const fulfillJson = async (route: Route, payload: unknown) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(payload),
    });
  };

  await page.route('**/api/integrity/services?**', (route) => fulfillJson(route, services));
  await page.route('**/api/integrity/services', (route) => fulfillJson(route, services));
  await page.route('**/api/integrity/registry?**', (route) => fulfillJson(route, registry));
  await page.route('**/api/integrity/registry', (route) => fulfillJson(route, registry));
  await page.route('**/api/integrity/tasks?**', (route) => fulfillJson(route, tasks));
  await page.route('**/api/integrity/tasks', (route) => fulfillJson(route, tasks));

  await page.route('**/api/integrity/services/baseline?**', (route) => fulfillJson(route, svcBaseline));
  await page.route('**/api/integrity/services/baseline', async (route) => {
    if (route.request().method() === 'POST') {
      try {
        const body = await route.request().postDataJSON();
        if (Array.isArray(body?.entries)) {
          svcBaseline.splice(0, svcBaseline.length, ...body.entries);
        }
      } catch {
        // ignore parse failures
      }
      await fulfillJson(route, { status: 'ok' });
      return;
    }
    await fulfillJson(route, svcBaseline);
  });

  await page.route('**/api/integrity/registry/baseline?**', (route) => fulfillJson(route, regBaseline));
  await page.route('**/api/integrity/registry/baseline', async (route) => {
    if (route.request().method() === 'POST') {
      try {
        const body = await route.request().postDataJSON();
        if (Array.isArray(body?.entries)) {
          regBaseline.splice(0, regBaseline.length, ...body.entries);
        }
      } catch {
        // ignore
      }
      await fulfillJson(route, { status: 'ok' });
      return;
    }
    await fulfillJson(route, regBaseline);
  });

  await page.route('**/api/integrity/tasks/baseline?**', (route) => fulfillJson(route, taskBaseline));
  await page.route('**/api/integrity/tasks/baseline', async (route) => {
    if (route.request().method() === 'POST') {
      try {
        const body = await route.request().postDataJSON();
        if (Array.isArray(body?.entries)) {
          taskBaseline.splice(0, taskBaseline.length, ...body.entries);
        }
      } catch {
        // ignore
      }
      await fulfillJson(route, { status: 'ok' });
      return;
    }
    await fulfillJson(route, taskBaseline);
  });

  await page.route('**/api/integrity/events?**', (route) =>
    fulfillJson(route, [
      {
        detected_at: '2024-01-01T00:00:00Z',
        severity: 'high',
        event_type: 'service_change',
        title: 'Service changed',
      },
    ])
  );

  await page.route('**/api/integrity/services/diff?**', (route) =>
    fulfillJson(route, {
      added: [{ name: 'svc-new' }],
      removed: [],
      changed: [],
    })
  );

  await page.route('**/api/integrity/registry/diff?**', (route) =>
    fulfillJson(route, {
      added: [],
      removed: [],
      modified: [
        {
          key: { path: 'SOFTWARE\\\\Tenantra', name: 'Enabled' },
          left: { value_data: '0' },
          right: { value_data: '1' },
        },
      ],
    })
  );

  await page.route('**/api/admin/settings/tenant', async (route) => {
    const method = route.request().method();
    if (method === 'GET') {
      await fulfillJson(route, tenantSettings);
      return;
    }
    if (method === 'PUT') {
      try {
        const body = await route.request().postDataJSON();
        if (body && typeof body === 'object') {
          Object.entries(body).forEach(([key, value]) => {
            const existing = tenantSettings.find((entry) => entry.key === key);
            if (existing) {
              existing.value = value;
            } else {
              tenantSettings.push({
                id: key,
                tenant_id: 1,
                key,
                value,
              });
            }
          });
        }
      } catch {
        // ignore
      }
      await fulfillJson(route, tenantSettings);
      return;
    }
    await route.continue();
  });
}

export async function stubAdminSettingsApis(page: Page): Promise<void> {
  const settings = [
    { id: 1, tenant_id: null, key: 'theme.colors.primary', value: '#1877F2' },
    { id: 2, tenant_id: null, key: 'worker.enabled', value: true },
    { id: 3, tenant_id: null, key: 'grafana.url', value: 'https://grafana.example.com' },
  ];
  const modules = [
    { id: 1, name: 'process_monitoring', category: 'Processes', phase: 10, enabled: true },
    { id: 2, name: 'integrity_core', category: 'Integrity', phase: 9, enabled: false },
  ];

  await page.route('**/api/admin/settings', async (route) => {
    const method = route.request().method();
    if (method === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(settings),
      });
      return;
    }
    if (method === 'PUT') {
      try {
        const body = await route.request().postDataJSON();
        if (body && typeof body === 'object') {
          Object.entries(body).forEach(([key, value]) => {
            const existing = settings.find((entry) => entry.key === key);
            if (existing) {
              existing.value = value;
            } else {
              settings.push({ id: key, tenant_id: null, key, value });
            }
          });
        }
      } catch {
        // ignore
      }
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(settings),
      });
      return;
    }
    await route.continue();
  });

  await page.route('**/api/admin/modules', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(modules),
    });
  });

  await page.route('**/api/admin/modules/bulk', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ enable: [], disable: [] }),
    });
  });
}
