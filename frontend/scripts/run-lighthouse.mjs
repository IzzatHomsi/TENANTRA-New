import { spawn } from 'node:child_process';
import http from 'node:http';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const PREVIEW_HOST = '127.0.0.1';
const PREVIEW_PORT = 4173;
const PREVIEW_URL = `http://${PREVIEW_HOST}:${PREVIEW_PORT}`;

function waitForServer(url, timeout = 20000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const check = () => {
      const req = http.get(url, (res) => {
        res.destroy();
        resolve();
      });
      req.on('error', (err) => {
        if (Date.now() - start > timeout) {
          reject(new Error(`Timed out waiting for ${url}: ${err}`));
        } else {
          setTimeout(check, 500);
        }
      });
    };
    check();
  });
}

async function run() {
  const preview = spawn('npx', ['vite', 'preview', '--host', PREVIEW_HOST, '--port', String(PREVIEW_PORT)], {
    stdio: 'inherit',
    env: { ...process.env, NODE_ENV: 'production' },
  });

  const cleanup = () => {
    if (!preview.killed) {
      preview.kill('SIGTERM');
    }
  };

  process.on('SIGINT', () => {
    cleanup();
    process.exit(1);
  });
  process.on('SIGTERM', () => {
    cleanup();
    process.exit(1);
  });

  try {
    await waitForServer(PREVIEW_URL);

    const budgetsPath = fileURLToPath(new URL('../lighthouse.budgets.json', import.meta.url));

    const lighthouse = spawn('npx', [
      'lighthouse',
      PREVIEW_URL,
      '--only-categories=performance',
      `--budgets-path=${budgetsPath}`,
      '--output=json',
      `--output-path=${path.resolve('lighthouse-report.json')}`,
      '--quiet',
      '--chrome-flags=--headless=new --no-sandbox',
    ], {
      stdio: 'inherit',
      env: { ...process.env, CI: '1' },
    });

    await new Promise((resolve, reject) => {
      lighthouse.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error(`Lighthouse exited with code ${code}`));
      });
    });
  } finally {
    cleanup();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
