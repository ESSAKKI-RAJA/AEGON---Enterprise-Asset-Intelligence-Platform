import { test, expect } from "@playwright/test";

test.describe("Dashboard Module", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "user0@aegon.test");
    await page.fill('input[type="password"]', "StrongPass1!");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/dashboard", { timeout: 15000 });
  });

  test("Dashboard loads successfully", async ({ page }) => {
    // Wait for the Dashboard title to be visible
    await expect(
      page
        .locator("h1")
        .filter({ hasText: /Dashboard|Overview/i })
        .first(),
    ).toBeVisible({ timeout: 10000 });

    // Ensure there's no "Failed to load dashboard" or similar error
    await expect(page.getByText(/Failed to load/i)).toHaveCount(0);
  });
});
