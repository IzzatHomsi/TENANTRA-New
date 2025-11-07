import { test, expect, Page } from "@playwright/test";

const API_BASE = (process.env.PLAYWRIGHT_API_BASE || "").replace(/\/$/, "");

function apiMatchers(path: string): string[] {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const patterns = [`**${normalized}`];
  if (API_BASE) {
    const candidate = `${API_BASE}${normalized}`;
    if (!patterns.includes(candidate)) {
      patterns.push(candidate);
    }
  }
  return patterns;
}

async function routeApi(page: Page, path: string, handler: Parameters<Page["route"]>[1]): Promise<void> {
  for (const pattern of apiMatchers(path)) {
    await page.route(pattern, handler);
  }
}

const modules = [
  {
    id: 1,
    name: "network_device_health",
    category: "Network & Perimeter Security",
    phase: 8,
    impact_level: "high",
    status: "active",
    checksum: "abc",
    description: "Network health checks",
    parameter_schema: { type: "object", properties: {} },
    has_runner: true,
    enabled: true,
    enabled_global: true,
    last_update: null,
  },
  {
    id: 2,
    name: "pci_dss_check",
    category: "Security & Compliance",
    phase: 7,
    impact_level: "high",
    status: "active",
    checksum: "def",
    description: "PCI scan",
    parameter_schema: { type: "object", properties: {} },
    has_runner: true,
    enabled: true,
    enabled_global: true,
    last_update: null,
  },
];

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("token", "demo-token");
    localStorage.setItem("user", JSON.stringify({ username: "admin" }));
    localStorage.setItem("role", "admin");
  });

  await routeApi(page, "/auth/me", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ user: { id: 1, username: "admin" }, role: "admin" }),
    });
  });

  await routeApi(page, "/modules/", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(modules),
    });
  });

  await routeApi(page, "/schedules?module_id=2", (route) => {
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
  });
});


test("module catalog search and category filters", async ({ page }) => {
  await page.goto("/app/modules");

  await expect(page.getByRole("button", { name: "network_device_health" })).toBeVisible();
  await expect(page.getByRole("button", { name: "pci_dss_check" })).toBeVisible();

  const filterSelects = page.locator("select");
  await filterSelects.nth(0).selectOption({ label: "Security & Compliance" });
  await expect(page.getByRole("button", { name: "pci_dss_check" })).toBeVisible();
  await expect(page.getByRole("button", { name: "network_device_health" })).toHaveCount(0);

  await filterSelects.nth(0).selectOption("");

  await page.fill("input[placeholder='Search modules']", "pci");
  await expect(page.getByRole("button", { name: "pci_dss_check" })).toBeVisible();
  await expect(page.getByRole("button", { name: "network_device_health" })).toHaveCount(0);
});

