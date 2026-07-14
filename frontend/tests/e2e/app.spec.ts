import { test, expect } from "@playwright/test";

test.describe("AEGON Enterprise Platform - E2E Acceptance Test", () => {
  test.beforeEach(async ({ page }) => {
    // Perform a real login flow to acquire the JWT token
    await page.goto("/login");
    await page.fill('input[type="email"]', "user0@aegon.test");
    await page.fill('input[type="password"]', "StrongPass1!");
    await page.click('button[type="submit"]');

    // Wait for the redirect to the dashboard
    await page.waitForURL("**/dashboard", { timeout: 15000 });
  });

  test("Core Modules Load Successfully", async ({ page }) => {
    // Ensure we are on the Dashboard
    await expect(
      page
        .locator("h1")
        .filter({ hasText: /Dashboard|Overview/i })
        .first(),
    ).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/Failed to load/i)).toHaveCount(0);

    // Sidebar navigation items to test
    const modules = [
      { name: "Assets", titlePattern: /Asset Registry|Assets/i },
      { name: "Maintenance", titlePattern: /Maintenance|Work Orders/i },
      { name: "Inventory", titlePattern: /Inventory/i },
      { name: "Procurement", titlePattern: /Procurement/i },
      { name: "Finance", titlePattern: /Finance/i },
      { name: "Analytics", titlePattern: /Analytics/i },
      { name: "AI Intelligence", titlePattern: /AI Intelligence|Recommendations/i },
      { name: "Settings", titlePattern: /Settings|Profile/i },
    ];

    for (const mod of modules) {
      // Click the sidebar link
      const link = page
        .locator("nav")
        .getByRole("link", { name: new RegExp(`^${mod.name}$`, "i") });
      if ((await link.count()) > 0) {
        await link.click();

        // Wait for the specific page title to be visible
        await expect(page.locator("h1").filter({ hasText: mod.titlePattern }).first()).toBeVisible({
          timeout: 15000,
        });

        // Ensure no "Failed to load" text is visible on any of the module pages
        await expect(page.getByText(/Failed to load/i)).toHaveCount(0);
      }
    }
  });
});
