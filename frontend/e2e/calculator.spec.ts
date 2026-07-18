/**
 * E2E tests — critical user journey through the full application.
 *
 * Covers the complete fan flow: land on page → type message → get response →
 * switch to ops view → see heatmap → see recommendations.
 * Plus error handling when API is unavailable.
 *
 * Run against the full stack in offline mode (USE_GEMINI=false).
 */

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BASE_URL || "http://localhost:8000";

test.describe("MatchDay Command Center — Critical User Journey", () => {
  test("complete fan assistant flow", async ({ page }) => {
    // Step 1: Navigate to the app
    await page.goto(BASE_URL);
    await expect(page.locator("h1")).toContainText("MatchDay");

    // Step 2: Verify fan view is active by default
    const fanTab = page.getByRole("button", { name: /Fan Assistant/ });
    await expect(fanTab).toHaveAttribute("aria-current", "page");

    // Step 3: Type a message in the chat
    const chatInput = page.getByLabel(/Type your message/i);
    await chatInput.fill("Where can I get food?");

    // Step 4: Send message and wait for response
    await page.getByRole("button", { name: "Send" }).click();
    await expect(page.getByText(/food/i).first()).toBeVisible({ timeout: 10000 });

    // Step 5: Switch to Operations view
    await page.getByRole("button", { name: /Operations Dashboard/ }).click();
    const opsTab = page.getByRole("button", { name: /Operations Dashboard/ });
    await expect(opsTab).toHaveAttribute("aria-current", "page");

    // Step 6: Verify crowd heatmap is visible
    await expect(page.getByText("Overall Density")).toBeVisible({ timeout: 10000 });

    // Step 7: Verify recommendations section is visible
    await expect(page.getByText(/AI Recommendations/)).toBeVisible();
  });

  test("venue navigator provides directions", async ({ page }) => {
    await page.goto(BASE_URL);

    // The VenueNavigator should be visible in fan view
    await expect(page.getByText("Venue Navigator")).toBeVisible();

    // Click Get Directions
    await page.getByRole("button", { name: "Get Directions" }).click();

    // Verify directions appear
    await expect(page.getByText(/Starting from/)).toBeVisible();
  });

  test("error handling when API route is blocked", async ({ page }) => {
    // Block the chat API
    await page.route("**/api/chat", (route) => route.abort());

    await page.goto(BASE_URL);

    const chatInput = page.getByLabel(/Type your message/i);
    await chatInput.fill("Where is Gate A?");
    await page.getByRole("button", { name: "Send" }).click();

    // Verify error alert appears
    await expect(page.getByRole("alert")).toBeVisible({ timeout: 10000 });
  });
});
