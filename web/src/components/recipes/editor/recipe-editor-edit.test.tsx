import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { sampleRecipe } from "@/lib/recipes/recipe-fixture";
import { RecipeEditor } from "./recipe-editor";

const push = vi.fn();
const get = vi.fn();
const put = vi.fn();
const post = vi.fn();
const patch = vi.fn();
const del = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/api", async (orig) => ({
  ...(await orig<typeof import("@/lib/api")>()),
  api: {
    get: (...a: unknown[]) => get(...a),
    put: (...a: unknown[]) => put(...a),
    post: (...a: unknown[]) => post(...a),
    patch: (...a: unknown[]) => patch(...a),
    delete: (...a: unknown[]) => del(...a),
  },
}));

const CAT = sampleRecipe.category_id;

function renderEdit(onReload = vi.fn()) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <RecipeEditor mode="edit" recipe={sampleRecipe} onReload={onReload} />
    </QueryClientProvider>,
  );
  return userEvent.setup();
}

async function changeTitle(user: ReturnType<typeof userEvent.setup>, suffix: string) {
  await user.type(screen.getByLabelText("Tiêu đề"), suffix);
}

describe("RecipeEditor in edit mode", () => {
  beforeEach(() => {
    push.mockReset();
    get.mockReset().mockResolvedValue([{ id: CAT, name: "Món chính" }]);
    put.mockReset();
    post.mockReset();
    patch.mockReset();
    del.mockReset();
  });

  it("opens prefilled with the saved recipe", async () => {
    renderEdit();

    expect(screen.getByLabelText("Tiêu đề")).toHaveValue("Phở bò Hà Nội");
    expect(screen.getByLabelText("Tên nguyên liệu 1")).toHaveValue("Thịt bò");
    expect(screen.getByLabelText("Nội dung bước 1")).toHaveValue("Ninh xương\nNinh xương 3 giờ.");
    expect(screen.getByRole("button", { name: "Lưu thay đổi" })).toBeDisabled();
  });

  it("keeps the saved category selected once the category options have loaded", async () => {
    renderEdit();

    await waitFor(() =>
      expect(screen.getByRole("option", { name: "Món chính" })).toBeInTheDocument(),
    );
    expect(screen.getByLabelText("Danh mục")).toHaveValue(CAT);
  });

  it("saves the recipe with the loaded row version and reports success", async () => {
    put.mockResolvedValue({ ...sampleRecipe, title: "Phở bò Hà Nội (sửa)", row_version: 5 });
    const user = renderEdit();

    await changeTitle(user, " (sửa)");
    await user.click(screen.getByRole("button", { name: "Lưu thay đổi" }));

    await waitFor(() =>
      expect(put).toHaveBeenCalledWith(
        "/recipes/{recipe_id}",
        expect.objectContaining({
          path: { recipe_id: sampleRecipe.id },
          rowVersion: 4,
          body: expect.objectContaining({ title: "Phở bò Hà Nội (sửa)" }),
        }),
      ),
    );
    expect(await screen.findByText("Đã lưu thay đổi.")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
    expect(del).not.toHaveBeenCalled();
  });

  it("on conflict, shows the dialog and 'reload' replaces local edits with the newer version", async () => {
    put.mockRejectedValue(new ApiError(409, { title: "Conflict", detail: "stale" }));
    const latest = { ...sampleRecipe, title: "Phở bò (bản mới)", row_version: 9 };
    const onReload = vi.fn().mockResolvedValue(latest);
    const user = renderEdit(onReload);

    await changeTitle(user, " nháp");
    await user.click(screen.getByRole("button", { name: "Lưu thay đổi" }));
    const dialog = await screen.findByRole("alertdialog");

    await user.click(within(dialog).getByRole("button", { name: "Tải phiên bản mới" }));

    await waitFor(() => expect(screen.getByLabelText("Tiêu đề")).toHaveValue("Phở bò (bản mới)"));
    expect(onReload).toHaveBeenCalledTimes(1);
    expect(put).toHaveBeenCalledTimes(1);
  });

  it("on conflict, 'overwrite' re-saves local edits on top of the newer row version", async () => {
    put
      .mockRejectedValueOnce(new ApiError(409, { title: "Conflict", detail: "stale" }))
      .mockResolvedValueOnce({ ...sampleRecipe, row_version: 10 });
    const onReload = vi.fn().mockResolvedValue({ ...sampleRecipe, row_version: 9 });
    const user = renderEdit(onReload);

    await changeTitle(user, " của tôi");
    await user.click(screen.getByRole("button", { name: "Lưu thay đổi" }));
    const dialog = await screen.findByRole("alertdialog");
    await user.click(within(dialog).getByRole("button", { name: "Ghi đè bằng bản của tôi" }));

    await waitFor(() => expect(put).toHaveBeenCalledTimes(2));
    expect(put).toHaveBeenLastCalledWith(
      "/recipes/{recipe_id}",
      expect.objectContaining({
        rowVersion: 9,
        body: expect.objectContaining({ title: "Phở bò Hà Nội của tôi" }),
      }),
    );
    expect(await screen.findByText("Đã lưu thay đổi.")).toBeInTheDocument();
  });

  it("publishes a saved recipe in place and then offers to unpublish", async () => {
    patch.mockResolvedValue({ ...sampleRecipe, status: 1, row_version: 5 });
    const user = renderEdit();

    await user.click(screen.getByRole("button", { name: "Xuất bản" }));

    await waitFor(() =>
      expect(patch).toHaveBeenCalledWith("/recipes/{recipe_id}/publish", {
        path: { recipe_id: sampleRecipe.id },
      }),
    );
    expect(await screen.findByRole("button", { name: "Gỡ xuất bản" })).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });
});
