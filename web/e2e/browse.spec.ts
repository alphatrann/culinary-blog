import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { expectNoSeriousA11yViolations } from "./a11y";
import { type E2EState, STATE_FILE } from "./global-setup";

const state: E2EState = JSON.parse(readFileSync(STATE_FILE, "utf-8"));

test.describe("browse", () => {
  test("a guest finds a recipe from home through search", async ({ page }) => {
    await page.goto("/");
    await expectNoSeriousA11yViolations(page, "home");

    await page
      .getByRole("main")
      .getByRole("searchbox", { name: "Tìm công thức" })
      .fill(state.searchToken);
    await page.getByRole("main").getByRole("button", { name: "Tìm kiếm" }).click();
    await expect(page).toHaveURL(/\/search\?/);
    await expectNoSeriousA11yViolations(page, "search results");

    await page.getByRole("link", { name: state.recipeTitle }).first().click();
    await expect(page).toHaveURL(new RegExp(`/recipes/${state.recipeSlug}$`));
    await expect(page.getByRole("heading", { level: 1, name: state.recipeTitle })).toBeVisible();
    await expectNoSeriousA11yViolations(page, "recipe detail");
  });
});
