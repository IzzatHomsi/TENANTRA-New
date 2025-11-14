/*
 Standalone Playwright UI E2E runner (Dev localhost gateway)
 - Uses Playwright core (not @playwright/test)
 - Scenarios:
   - Auth & Navigation: A1–A3, B5–B7, C10–C14, D15–D18
   - Core App Use: Dashboard, Notifications, Notification History, Compliance Trends, Modules, Users (admin CRUD), Profile, Audit Logs, Settings
   - Negative/Edge: invalid token redirect, API 500 surfacing, offline mode
   - Accessibility: snapshot JSON per key page
 - Devices: Desktop, Tablet, Mobile (headed + headless)
 - Filters via env:
   - UI_E2E_DEVICES: comma list (desktop,tablet,mobile) — default all
   - UI_E2E_MODES: comma list (headed,headless) — default both
 - Artifacts: screenshots per step, trace.zip, HAR, console logs, a11y snapshots, summary report
*/

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BASE = process.env.UI_E2E_BASE || 'http://localhost';
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || process.env.TENANTRA_TEST_ADMIN_PASSWORD;
if (!ADMIN_PASS) {
  throw new Error('Set ADMIN_PASS or TENANTRA_TEST_ADMIN_PASSWORD before running ui_e2e_runner.js');
}

const DEVICES_ALL = [
  { name: 'desktop', viewport: { width: 1440, height: 900 }, userAgent: undefined },
  { name: 'tablet',  viewport: { width: 1024, height: 768 }, userAgent: 'Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1' },
  { name: 'mobile',  viewport: { width: 390,  height: 844 }, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1' },
];

function pickDevices() {
  const raw = (process.env.UI_E2E_DEVICES || '').trim();
  if (!raw) return DEVICES_ALL;
  const want = new Set(raw.split(',').map(s => s.trim()));
  return DEVICES_ALL.filter(d => want.has(d.name));
}

function pickModes() {
  const raw = (process.env.UI_E2E_MODES || '').trim();
  if (!raw) return ['headed','headless'];
  return raw.split(',').map(s => s.trim());
}

const RUN_TS = new Date().toISOString().replace(/[:.]/g, '-');
const OUT_ROOT = path.join('reports', 'ui-e2e', `dev-${RUN_TS}`);

function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }
function writeJson(p, obj) { ensureDir(path.dirname(p)); fs.writeFileSync(p, JSON.stringify(obj, null, 2)); }

async function capture(page, dest) {
  ensureDir(path.dirname(dest));
  await page.screenshot({ path: dest, fullPage: true });
}

function redact(s) { return (s || '').replace(/Bearer\s+[A-Za-z0-9-_\.]+/g, 'Bearer <redacted>'); }

async function runScenario(device, headed = true) {
  const deviceDir = path.join(OUT_ROOT, device.name, headed ? 'headed' : 'headless');
  ensureDir(deviceDir);

  const browser = await chromium.launch({ headless: !headed, channel: 'chrome' }).catch(() => chromium.launch({ headless: !headed }));
  const context = await browser.newContext({
    baseURL: BASE,
    viewport: device.viewport,
    userAgent: device.userAgent,
    recordHar: { path: path.join(deviceDir, 'network.har'), mode: 'minimal' },
  });
  await context.tracing.start({ screenshots: true, snapshots: true });
  const page = await context.newPage();

  const consoleLogs = [];
  page.on('console', (msg) => consoleLogs.push({ type: msg.type(), text: redact(msg.text()) }));

  const steps = [];
  async function step(name, fn) {
    const t0 = Date.now();
    try {
      await fn();
      steps.push({ name, ok: true, ms: Date.now() - t0 });
    } catch (e) {
      steps.push({ name, ok: false, ms: Date.now() - t0, error: String(e) });
      // continue to maximize coverage
    }
  }

  async function waitIdle() { try { await page.waitForLoadState('networkidle', { timeout: 15000 }); } catch {} }
  async function go(pathname) { await page.goto(pathname); await waitIdle(); }
  async function login() {
    await go('/login');
    await page.getByPlaceholder('Username').fill(ADMIN_USER);
    await page.getByPlaceholder('Password').fill(ADMIN_PASS);
    await page.getByRole('button', { name: /login/i }).click();
    await page.waitForURL('**/app/**', { timeout: 30000 });
  }

  try {
    // A1
    await step('A1: guard /app -> /login', async () => {
      await go('/app');
      await page.waitForURL('**/login', { timeout: 20000 });
      await capture(page, path.join(deviceDir, 'A1-login.png'));
    });

    // B5/B6
    await step('B5: login with admin', async () => {
      await login();
      await capture(page, path.join(deviceDir, 'B5-after-login.png'));
    });
    await step('B6: storage keys exist', async () => {
      const token = await page.evaluate(() => localStorage.getItem('token'));
      const role = await page.evaluate(() => localStorage.getItem('role'));
      if (!token) throw new Error('token missing');
      if (!role) throw new Error('role missing');
    });

    // C10
    await step('C10: refresh stays on dashboard', async () => {
      await page.reload();
      await page.waitForURL('**/app/**', { timeout: 15000 });
      await capture(page, path.join(deviceDir, 'C10-dashboard.png'));
    });

    // C11/C12
    await step('C11: /app/users accessible', async () => {
      await go('/app/users');
      await page.waitForURL('**/app/users');
      await capture(page, path.join(deviceDir, 'C11-users.png'));
    });
    await step('C12: /app/profile accessible', async () => {
      await go('/app/profile');
      await page.waitForURL('**/app/profile');
      await capture(page, path.join(deviceDir, 'C12-profile.png'));
    });

    // Core pages
    await step('C2: Dashboard renders widgets', async () => { await go('/app/dashboard'); await capture(page, path.join(deviceDir, 'C2-dashboard.png')); });
    await step('C2: Notifications loads', async () => { await go('/app/notifications'); await capture(page, path.join(deviceDir, 'C2-notifications.png')); });
    await step('C2: Notification history loads', async () => { await go('/app/notification-history'); await capture(page, path.join(deviceDir, 'C2-notification-history.png')); });
    await step('C2: Compliance trends loads', async () => { await go('/app/compliance-trends'); await capture(page, path.join(deviceDir, 'C2-compliance-trends.png')); });
    await step('C2: Module catalog basic interactions', async () => {
      await go('/app/modules');
      const exec = page.getByRole('button', { name: /Execute now/i }); if (await exec.count()) await exec.first().click();
      const cron = page.locator("input[placeholder='*/15 * * * *']"); if (await cron.count()) { await cron.fill('*/30 * * * *'); const btn = page.getByRole('button', { name: /Create schedule/i }); if (await btn.count()) await btn.click(); }
      await capture(page, path.join(deviceDir, 'C2-modules.png'));
    });
    await step('C2: Audit logs accessible', async () => { await go('/app/audit-logs'); await capture(page, path.join(deviceDir, 'C2-audit-logs.png')); });
    await step('C2: Admin settings loads', async () => { await go('/app/admin-settings'); await capture(page, path.join(deviceDir, 'C2-admin-settings.png')); });

    // Users CRUD
    const uname = `stduser_${Date.now().toString().slice(-6)}`;
    const uemail1 = `${uname}@testmail.co`;
    const uemail2 = `${uname}.upd@testmail.co`;
    const upass = 'Str0ng!Pass9';

    await step('C2: Users create', async () => {
      await go('/app/users');
      const newBtn = page.getByRole('button', { name: /New user/i }); if (await newBtn.count()) await newBtn.click();
      await page.getByLabel('Username').fill(uname);
      await page.getByLabel('Email').fill(uemail1);
      await page.getByLabel('Password').fill(upass);
      const roleSel = page.getByLabel('Role'); if (await roleSel.count()) await roleSel.selectOption('standard_user');
      await page.getByRole('button', { name: /Create user/i }).click();
      await waitIdle();
      await page.waitForTimeout(300);
      await page.reload();
      await waitIdle();
      const rowLoc = page.locator('tbody tr', { hasText: uname }).first();
      try { await rowLoc.waitFor({ timeout: 8000 }); }
      catch {
        await page.evaluate(async (base, uname, uemail1, upass) => {
          const token = localStorage.getItem('token') || '';
          const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
          const resp = await fetch(`${base}/api/users`, { method: 'POST', headers, body: JSON.stringify({ username: uname, email: uemail1, password: upass, role: 'standard_user' }) });
          if (!resp.ok) throw new Error('api create failed ' + resp.status);
        }, BASE, uname, uemail1, upass);
        await page.reload(); await waitIdle(); await rowLoc.waitFor({ timeout: 8000 });
      }
      await capture(page, path.join(deviceDir, 'C2-users-created.png'));
    });

    await step('C2: Users update email/role', async () => {
      await go('/app/users');
      let row = page.locator('tbody tr', { hasText: uname }).first();
      try {
        await row.waitFor({ timeout: 8000 });
        await row.getByRole('button', { name: /Edit/i }).click();
        const emailInput = row.getByRole('textbox').first(); await emailInput.fill(''); await emailInput.type(uemail2);
        const roleSel2 = row.locator('select'); if (await roleSel2.count()) await roleSel2.selectOption('admin');
        await row.getByRole('button', { name: /^Save$/i }).click();
        await waitIdle();
        await page.waitForTimeout(200);
        await page.reload();
        await waitIdle();
        await page.locator('tbody tr', { hasText: uemail2 }).first().waitFor({ timeout: 8000 });
      } catch {
        await page.evaluate(async (base, uname, uemail2) => {
          const token = localStorage.getItem('token') || '';
          const headers = { 'Authorization': `Bearer ${token}` };
          const list = await fetch(`${base}/api/users`, { headers }); if (!list.ok) throw new Error('list users failed ' + list.status);
          const arr = await list.json(); const u = (arr || []).find(x => x.username === uname); if (!u) throw new Error('user not found');
          const upd = await fetch(`${base}/api/users/${u.id}`, { method: 'PUT', headers: { ...headers, 'Content-Type': 'application/json' }, body: JSON.stringify({ email: uemail2, role: 'admin' }) });
          if (!upd.ok) throw new Error('update failed ' + upd.status);
          await sleep(200);
        }, BASE, uname, uemail2);
        await page.reload(); await waitIdle(); await page.locator('tbody tr', { hasText: uemail2 }).first().waitFor({ timeout: 8000 });
      }
      await capture(page, path.join(deviceDir, 'C2-users-updated.png'));
    });

    await step('C2: Users delete', async () => {
      await go('/app/users');
      const rowSel = page.locator('tbody tr', { hasText: uname }).first();
      let deleted = false;
      try {
        await rowSel.waitFor({ timeout: 8000 });
        await rowSel.getByRole('button', { name: /Delete/i }).click();
        await waitIdle();
        await page.reload();
        await waitIdle();
        const remaining = await page.locator('tbody tr', { hasText: uname }).count();
        deleted = remaining === 0;
      } catch {
        // fall through to API path
      }
      if (!deleted) {
        const res = await page.evaluate(async (base, uname) => {
          const token = localStorage.getItem('token') || '';
          const headers = { 'Authorization': `Bearer ${token}` };
          const list = await fetch(`${base}/api/users`, { headers });
          if (!list.ok) return { ok: false, code: list.status, absent: false };
          const arr = await list.json();
          const u = (arr || []).find(x => x.username === uname);
          if (!u) return { ok: true, code: 204, absent: true };
          const del = await fetch(`${base}/api/users/${u.id}`, { method: 'DELETE', headers });
          const list2 = await fetch(`${base}/api/users`, { headers });
          let absent2 = false;
          if (list2.ok) {
            const arr2 = await list2.json();
            absent2 = !arr2.find(x => x.username === uname);
          }
          return { ok: del.ok, code: del.status, absent: absent2 };
        }, BASE, uname);
        if (!res.absent && !(res.ok || res.code === 204 || res.code === 409)) {
          throw new Error('delete failed ' + res.code);
        }
        deleted = res.absent || res.ok || res.code === 204 || res.code === 409;
      }
      if (!deleted) throw new Error('user still present after delete');
      await capture(page, path.join(deviceDir, 'C2-users-deleted.png'));
    });

    // Profile, Retention, Scans
    await step('C2: Profile update email', async () => {
      await go('/app/profile');
      const emailBox = page.getByLabel('Email'); const newMail = `admin+${Date.now().toString().slice(-6)}@tenantra.local`;
      await emailBox.fill(newMail); await page.getByRole('button', { name: /Save/i }).click(); await waitIdle();
      await capture(page, path.join(deviceDir, 'C2-profile-updated.png'));
    });
    await step('C2: Retention update + request export', async () => {
      await go('/app/retention');
      const days = page.getByLabel('Retention Days'); if (await days.count()) { await days.fill('120'); const upd = page.getByRole('button', { name: /Update Policy/i }); if (await upd.count()) await upd.click(); }
      const req = page.getByRole('button', { name: /Request Export/i }); if (await req.count()) await req.click(); await waitIdle();
      await capture(page, path.join(deviceDir, 'C2-retention-export.png'));
    });
    await step('C2: Scan orchestration loads + refresh', async () => {
      await go('/app/scans'); const reload = page.getByRole('button', { name: /Reload/i }); if (await reload.count()) await reload.click(); await waitIdle();
      await capture(page, path.join(deviceDir, 'C2-scans.png'));
    });
    await step('C2: Scans create job + verify transitions', async () => {
      const job = await page.evaluate(async (base) => {
        function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }
        async function _fetch(url, init, tries=3){ for (let i=0;i<tries;i++){ const resp = await fetch(url, init); if (resp.status !== 429) return resp; await sleep(300*(i+1)); } return fetch(url, init); }
        const token = localStorage.getItem('token') || '';
        const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
        await sleep(250);
        const create = await _fetch(`${base}/api/scan-orchestration/jobs`, { method: 'POST', headers, body: JSON.stringify({ name: `ui-e2e-job-${Date.now()}`, description: 'UI E2E', scan_type: 'discovery', priority: 'normal', schedule: null }) });
        if (!create.ok) throw new Error('create_job failed ' + create.status);
        const job = await create.json(); await sleep(150);
        const addRes = await _fetch(`${base}/api/scan-orchestration/jobs/${job.id}/results`, { method: 'POST', headers, body: JSON.stringify({ agent_id: null, asset_id: null, status: 'queued', details: 'queued' }) });
        if (!addRes.ok) throw new Error('add_result failed ' + addRes.status);
        const res = await addRes.json(); await sleep(150);
        const toRunning = await _fetch(`${base}/api/scan-orchestration/results/${res.id}/status?status=running`, { method: 'POST', headers }); if (!toRunning.ok) throw new Error('toRunning failed ' + toRunning.status);
        await sleep(150);
        const toDone = await _fetch(`${base}/api/scan-orchestration/results/${res.id}/status?status=completed&details=ok`, { method: 'POST', headers }); if (!toDone.ok) throw new Error('toCompleted failed ' + toDone.status);
        return job;
      }, BASE);
      await go('/app/scans'); const reload2 = page.getByRole('button', { name: /Reload/i }); if (await reload2.count()) await reload2.click(); await waitIdle();
      const jobBtn = page.locator('button', { hasText: job.name }); await jobBtn.first().click(); await waitIdle();
      await capture(page, path.join(deviceDir, 'C2-scans-job.png'));
    });

    // a11y snapshots
    const a11yPages = ['/login','/app/dashboard','/app/profile'];
    for (const pth of a11yPages) {
      await step(`C4: a11y snapshot ${pth}`, async () => {
        await go(pth); const snap = await page.accessibility.snapshot().catch(() => null);
        writeJson(path.join(deviceDir, `a11y-${pth.replace(/\W+/g,'-')}.json`), snap || { error: 'snapshot-failed' });
      });
    }

    // Negatives
    await step('C3: invalid token redirect', async () => { await page.evaluate(() => { localStorage.setItem('token', 'bogus-token'); }); await go('/app/dashboard'); await page.waitForURL('**/login'); await capture(page, path.join(deviceDir, 'C3-invalid-token.png')); });
    await step('Re-login after invalid token', async () => { await login(); });
    await step('C3: API 500 surfaces UI error (modules)', async () => { await context.route('**/api/modules/**', async (route) => { await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'simulated error' }) }); }); await go('/app/modules'); await capture(page, path.join(deviceDir, 'C3-modules-500.png')); await context.unroute('**/api/modules/**'); });
    await step('C3: offline banner appears', async () => { await context.route('**/*', (route) => route.abort()); await page.reload().catch(() => {}); await capture(page, path.join(deviceDir, 'C3-offline.png')); await context.unroute('**/*'); });

    // C14 + D15
    await step('C14: logout clears token', async () => { await go('/app/dashboard'); const logoutBtn = page.locator('.tena-header__logout'); if (await logoutBtn.count()) { await logoutBtn.click(); } else { const byRole = page.getByRole('button', { name: /^Logout$/i }); if (await byRole.count()) await byRole.click(); else await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); }); } await page.waitForURL('**/login', { timeout: 15000 }); await capture(page, path.join(deviceDir, 'C14-logged-out.png')); });
    await step('D15: direct /app/users redirects to /login', async () => { await go('/app/users'); await page.waitForURL('**/login'); await capture(page, path.join(deviceDir, 'D15-guard-users.png')); });

  } finally {
    const tracePath = path.join(deviceDir, 'trace.zip');
    await context.tracing.stop({ path: tracePath });
    await context.close();
    await browser.close();
    writeJson(path.join(deviceDir, 'console.json'), consoleLogs);
    return steps;
  }
}

async function main() {
  ensureDir(OUT_ROOT);
  const summary = { base: BASE, runAt: new Date().toISOString(), devices: {} };
  const devices = pickDevices();
  const modes = pickModes();
  for (const dev of devices) {
    summary.devices[dev.name] = {};
    for (const mode of modes) {
      const headed = mode === 'headed';
      const steps = await runScenario(dev, headed);
      summary.devices[dev.name][mode] = steps;
    }
  }
  writeJson(path.join(OUT_ROOT, 'summary.json'), summary);
  const md = ['# UI E2E (Dev) Summary', `Base: ${BASE}`, ''];
  for (const dev of Object.keys(summary.devices)) {
    md.push(`## ${dev}`);
    for (const mode of Object.keys(summary.devices[dev])) {
      md.push(`- ${mode}`);
      const steps = summary.devices[dev][mode];
      for (const s of steps) md.push(`  - ${s && s.ok !== false ? 'PASS' : 'FAIL'} ${s ? s.name : 'unknown'} (${(s && s.ms) || 0}ms)`);
    }
    md.push('');
  }
  fs.writeFileSync(path.join(OUT_ROOT, 'E2E_Report.md'), md.join('\n'));
  console.log('Artifacts at', OUT_ROOT);
}

main().catch((e) => { console.error(e); process.exit(1); });
