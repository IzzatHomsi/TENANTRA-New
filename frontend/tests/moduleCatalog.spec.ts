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

const modulePayload = {
  id: 1,
  external_id: "net-001",
  name: "network_device_health",
  category: "Network & Perimeter Security",
  phase: 8,
  impact_level: "high",
  status: "active",
  checksum: "abc",
  description: "Network health checks",
  purpose: "Ensure core interfaces remain reachable",
  dependencies: "SNMP credentials",
  preconditions: "SNMP read access",
  team: "Network",
  operating_systems: "IOS",
  application_target: "core",
  compliance_mapping: "PCI",
  parameter_schema: {
    type: "object",
    properties: {
      targets: { type: "array", description: "Targets" },
    },
  },
  has_runner: true,
  enabled: true,
  enabled_global: true,
  last_update: null,
};

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
      body: JSON.stringify([modulePayload]),
    });
  });

  let scheduleState: "empty" | "single" = "empty";

  await routeApi(page, "/schedules?module_id=1", (route) => {
    if (scheduleState === "single") {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: 77,
            tenant_id: 1,
            module_id: 1,
            agent_id: null,
            cron_expr: "*/30 * * * *",
            status: "scheduled",
            enabled: true,
            last_run_at: null,
            next_run_at: new Date().toISOString(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ]),
      });
      return;
    }
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
  });

  await routeApi(page, "/module-runs/1", (route, request) => {
    if (request.method() === "POST") {
      route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          id: 99,
          module_id: 1,
          tenant_id: 1,
          agent_id: null,
          status: "success",
          details: { message: "ok" },
          recorded_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }),
      });
      return;
    }
    route.continue();
  });

  let moduleEnabled = true;
  await routeApi(page, "/modules/1", (route, request) => {
    if (request.method() === "PUT") {
      moduleEnabled = !moduleEnabled;
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ...modulePayload, enabled: moduleEnabled }),
      });
      return;
    }
    route.continue();
  });

  await routeApi(page, "/schedules", (route, request) => {
    if (request.method() === "POST") {
      scheduleState = "single";
      route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          id: 77,
          tenant_id: 1,
          module_id: 1,
          agent_id: null,
          cron_expr: "*/30 * * * *",
          status: "scheduled",
          enabled: true,
          last_run_at: null,
          next_run_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }),
      });
      return;
    }
    route.continue();
  });

  await routeApi(page, "/schedules/77", (route, request) => {
    if (request.method() === "DELETE") {
      scheduleState = "empty";
      route.fulfill({ status: 204, body: "" });
      return;
    }
    route.continue();
  });
});


test("module catalog flows", async ({ page }) => {
  await page.goto("/app/modules");

  await expect(page.getByRole("heading", { name: "Module Catalog" })).toBeVisible();
  await expect(page.getByRole("button", { name: "network_device_health" })).toBeVisible();

  const toggleButton = page.getByRole("button", { name: /^(Disable|Enable)$/ });
  await expect(toggleButton).toHaveText("Disable");

  await toggleButton.click();
  await expect(toggleButton).toHaveText("Enable");

  await toggleButton.click();
  await expect(toggleButton).toHaveText("Disable");

  await page.getByRole("button", { name: "Execute now" }).click();
  await expect(page.getByText(/Run recorded/)).toBeVisible();

  await page.getByLabel("Cron Expression").fill("*/30 * * * *");
  await page.getByRole("button", { name: "Create schedule" }).click();
  await expect(page.getByText("Schedule created.")).toBeVisible();
  await expect(page.getByText("*/30 * * * *")).toBeVisible();

  const removeButton = page.getByRole("button", { name: "Remove" });
  await removeButton.click();
  await expect(page.getByText("Schedule removed.")).toBeVisible();
  await expect(page.getByText("No schedules defined for this module.")).toBeVisible();
});

