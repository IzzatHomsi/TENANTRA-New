import { promises as fs } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const assetsDir = path.resolve(__dirname, "../dist/assets");

const budgets = [
  {
    label: "app shell JS",
    pattern: /^index-.*\.js$/,
    budgetKb: Number(process.env.BUNDLE_BUDGET_APP_KB || 240),
  },
  {
    label: "api client JS",
    pattern: /^apiClient-.*\.js$/,
    budgetKb: Number(process.env.BUNDLE_BUDGET_API_KB || 80),
  },
  {
    label: "global CSS",
    pattern: /^index-.*\.css$/,
    budgetKb: Number(process.env.BUNDLE_BUDGET_CSS_KB || 90),
  },
];

function formatSize(bytes) {
  return `${(bytes / 1024).toFixed(2)} kB`;
}

async function main() {
  let files;
  try {
    files = await fs.readdir(assetsDir);
  } catch (error) {
    console.error(`Bundle budget check failed: unable to read ${assetsDir}`);
    console.error(error);
    process.exit(1);
  }

  const results = [];
  const failures = [];

  for (const budget of budgets) {
    const candidates = files.filter((file) => budget.pattern.test(file));
    if (candidates.length === 0) {
      results.push({ budget, status: "skipped", message: "No matching files." });
      continue;
    }
    const target = candidates.sort().reverse()[0];
    const stats = await fs.stat(path.join(assetsDir, target));
    const sizeKb = stats.size / 1024;
    const passed = sizeKb <= budget.budgetKb;
    const message = `${budget.label}: ${formatSize(stats.size)} (budget ${budget.budgetKb} kB)`;
    results.push({ budget, status: passed ? "pass" : "fail", message, file: target });
    if (!passed) {
      failures.push({ budget, message, file: target });
    }
  }

  for (const { message, file, status } of results) {
    const prefix = status === "fail" ? "✖" : status === "pass" ? "✓" : "•";
    console.log(`${prefix} ${message}${file ? ` — ${file}` : ""}`);
  }

  if (failures.length > 0) {
    console.error("\nBundle budgets exceeded:");
    for (const fail of failures) {
      console.error(` - ${fail.message} (${fail.file})`);
    }
    process.exit(1);
  }

  console.log("\nBundle budgets within limits ✅");
}

main();
