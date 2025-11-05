// Lightweight evidence writer for Playwright run
import fs from 'fs';
import path from 'path';

export function ensureDir(p: string) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

export function writeText(filePath: string, data: string) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, data, 'utf-8');
}

export function writeJSON(filePath: string, obj: any) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(obj, null, 2), 'utf-8');
}
