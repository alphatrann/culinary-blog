import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { RecipeEditor } from "./recipe-editor";

const push = vi.fn();
const get = vi.fn();
const post = vi.fn();
const patch = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/api", async (orig) => ({
  ...(await orig<typeof import("@/lib/api")>()),
  api: {
    get: (...a: unknown[]) => get(...a),
    post: (...a: unknown[]) => post(...a),
    patch: (...a: unknown[]) => patch(...a),
  },
}));

const CAT = "7d9b0c3e-2f5a-4c1e-9a7b-1b2c3d4e5f60";

async function setup() {
  const user = userEvent.setup();
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <RecipeEditor />
    </QueryClientProvider>,
  );
  await screen.findByRole("option", { name: "Món chính" });
  return user;
}

async function fillBasics(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText("Tiêu đề"), "Phở bò Hà Nội");
  await user.type(screen.getByLabelText("Mô tả"), "Món phở truyền thống.");
  await user.selectOptions(screen.getByLabelText("Danh mục"), CAT);
  await user.type(screen.getByLabelText("Chuẩn bị (phút)"), "30");
  await user.type(screen.getByLabelText("Nấu (phút)"), "180");
  await user.type(screen.getByLabelText("Khẩu phần"), "4");
}

async function fillContent(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText("Tên nguyên liệu 1"), "Thịt bò");
  await user.type(screen.getByLabelText("Nội dung bước 1"), "Ninh xương");
}

describe("RecipeEditor", () => {
  beforeEach(() => {
    push.mockReset();
    post.mockReset();
    patch.mockReset();
    get.mockReset().mockResolvedValue([{ id: CAT, name: "Món chính" }]);
  });

  it("disables publish until there is an ingredient and a step", async () => {
    const user = await setup();
    const publish = screen.getByRole("button", { name: "Xuất bản" });
    expect(publish).toBeDisabled();
    expect(screen.getByRole("alert")).toHaveTextContent("ít nhất 1 nguyên liệu");
    await fillContent(user);
    expect(publish).toBeEnabled();
  });

  it("adds, removes and numbers steps", async () => {
    const user = await setup();
    await user.click(screen.getByRole("button", { name: "Thêm bước" }));
    expect(screen.getByLabelText("Nội dung bước 2")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Xóa bước 2" }));
    expect(screen.queryByLabelText("Nội dung bước 2")).not.toBeInTheDocument();
  });

  it("shows validation errors and does not submit", async () => {
    const user = await setup();
    await user.click(screen.getByRole("button", { name: "Lưu nháp" }));
    expect(await screen.findByText("Tiêu đề cần từ 5 đến 200 ký tự.")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("saves a draft with the mapped payload", async () => {
    post.mockResolvedValue({ id: "r1", slug: "pho-bo" });
    const user = await setup();
    await fillBasics(user);
    await fillContent(user);
    await user.click(screen.getByRole("button", { name: "Lưu nháp" }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard/recipes"));
    expect(post).toHaveBeenCalledWith("/recipes", {
      body: expect.objectContaining({
        title: "Phở bò Hà Nội",
        category_id: CAT,
        difficulty: 1,
        servings: 4,
        ingredients: [{ name: "Thịt bò", quantity: null, unit: null, order_index: 0 }],
        steps: [{ title: "Ninh xương", description: "Ninh xương" }],
      }),
    });
    expect(patch).not.toHaveBeenCalled();
  });

  it("publishes and goes to the recipe page", async () => {
    post.mockResolvedValue({ id: "r1", slug: "pho-bo" });
    patch.mockResolvedValue({ id: "r1", slug: "pho-bo" });
    const user = await setup();
    await fillBasics(user);
    await fillContent(user);
    await user.click(screen.getByRole("button", { name: "Xuất bản" }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/recipes/pho-bo"));
    expect(patch).toHaveBeenCalledWith("/recipes/{recipe_id}/publish", {
      path: { recipe_id: "r1" },
    });
  });

  it("keeps the draft and retries only publish after a 422", async () => {
    post.mockResolvedValue({ id: "r1", slug: "pho-bo" });
    patch
      .mockRejectedValueOnce(
        new ApiError(422, { detail: "Recipe phải có ít nhất 1 nguyên liệu và 1 bước thực hiện." }),
      )
      .mockResolvedValueOnce({ id: "r1", slug: "pho-bo" });
    const user = await setup();
    await fillBasics(user);
    await fillContent(user);
    await user.click(screen.getByRole("button", { name: "Xuất bản" }));
    expect(await screen.findByText(/Đã lưu bản nháp nhưng chưa xuất bản được/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Xuất bản" }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/recipes/pho-bo"));
    expect(post).toHaveBeenCalledOnce();
  });

  it("maps API field errors onto the form", async () => {
    post.mockRejectedValue(
      new ApiError(422, {
        errors: [{ loc: ["body", "title"], msg: "Tiêu đề đã tồn tại.", type: "value_error" }],
      }),
    );
    const user = await setup();
    await fillBasics(user);
    await fillContent(user);
    await user.click(screen.getByRole("button", { name: "Lưu nháp" }));
    expect(await screen.findByText("Tiêu đề đã tồn tại.")).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });
});
