import { expect, test } from "@playwright/test";
import { expectNoSeriousA11yViolations } from "./a11y";

const PASSWORD = "E2e-pass-2026!";

test.describe("author", () => {
  test("register, write a recipe, publish it, and see it on the public page", async ({ page }) => {
    const stamp = Date.now();
    const title = `E2E Phở bò ${stamp}`;

    await page.goto("/auth/register");
    await page.getByLabel("Tên hiển thị").fill("E2E Author");
    await page.getByLabel("Email").fill(`e2e-author-${stamp}@example.com`);
    await page.getByLabel("Mật khẩu", { exact: true }).fill(PASSWORD);
    await page.getByRole("button", { name: "Tạo tài khoản" }).click();
    await expect(page).not.toHaveURL(/\/auth\/register/);

    await page.goto("/dashboard/recipes/new");
    await expectNoSeriousA11yViolations(page, "create recipe");

    await page.getByLabel("Tiêu đề").fill(title);
    await page.getByLabel("Mô tả").fill("Phở bò Hà Nội theo cách nấu của gia đình.");
    await page.getByLabel("Danh mục").selectOption({ index: 1 });
    await page.getByLabel("Chuẩn bị (phút)").fill("30");
    await page.getByLabel("Nấu (phút)").fill("120");
    await page.getByLabel("Khẩu phần").fill("4");
    await page.getByLabel("Tên nguyên liệu 1").fill("Thịt bò");
    await page.getByLabel("Số lượng nguyên liệu 1").fill("500");
    await page.getByLabel("Đơn vị nguyên liệu 1").fill("g");
    await page.getByLabel("Nội dung bước 1").fill("Ninh xương bò 3 giờ.");

    await page.getByRole("button", { name: "Xuất bản" }).click();

    await expect(page).toHaveURL(/\/recipes\/[a-z0-9-]+$/);
    await expect(page.getByRole("heading", { level: 1, name: title })).toBeVisible();
    await expectNoSeriousA11yViolations(page, "published recipe");
  });
});
