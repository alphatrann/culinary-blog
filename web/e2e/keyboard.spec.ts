import { expect, test } from "@playwright/test";

test.describe("keyboard", () => {
  test("skip link is the first tab stop and moves focus into the page content", async ({
    page,
  }) => {
    await page.goto("/");

    await page.keyboard.press("Tab");
    const skip = page.getByRole("link", { name: "Chuyển đến nội dung" });
    await expect(skip).toBeFocused();
    await expect(skip).toBeVisible();

    await page.keyboard.press("Enter");
    await expect(page.locator("#content")).toBeFocused();
  });
});
