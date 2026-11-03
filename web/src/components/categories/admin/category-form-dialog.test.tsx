import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi, type MockInstance } from "vitest";
import { api, ApiError } from "@/lib/api";
import { CategoryFormDialog, type AdminCategory } from "./category-form-dialog";

let post: MockInstance<typeof api.post>;
let put: MockInstance<typeof api.put>;

const existing: AdminCategory = {
  id: "5b1f0c7e-0000-4000-8000-000000000002",
  name: "Món chính",
  slug: "mon-chinh",
  description: "Các món ăn chính",
  image_url: null,
  recipe_count: 3,
};

function setup(category?: AdminCategory) {
  const user = userEvent.setup();
  render(
    <QueryClientProvider client={new QueryClient()}>
      <CategoryFormDialog open category={category} onOpenChange={vi.fn()} />
    </QueryClientProvider>,
  );
  return user;
}

describe("CategoryFormDialog", () => {
  beforeEach(() => {
    post = vi.spyOn(api, "post");
    put = vi.spyOn(api, "put");
  });
  afterEach(() => vi.restoreAllMocks());

  it("rejects a too-short name without calling the API", async () => {
    const user = setup();
    await user.type(screen.getByLabelText("Tên danh mục"), "x");
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    expect(await screen.findByText("Tên danh mục cần từ 2 đến 50 ký tự.")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("rejects HTML in the name", async () => {
    const user = setup();
    await user.type(screen.getByLabelText("Tên danh mục"), "<b>Bánh</b>");
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    expect(await screen.findByText("Tên danh mục không được chứa thẻ HTML.")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("creates a category, sending null for empty optional fields", async () => {
    post.mockResolvedValue({ ...existing, name: "Tráng miệng" });
    const user = setup();
    await user.type(screen.getByLabelText("Tên danh mục"), "Tráng miệng");
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    await waitFor(() =>
      expect(post).toHaveBeenCalledWith("/categories", {
        body: { name: "Tráng miệng", description: null, image_url: null },
      }),
    );
  });

  it("edits an existing category with PUT and keeps its values prefilled", async () => {
    put.mockResolvedValue({ ...existing, description: null });
    const user = setup(existing);
    expect(screen.getByLabelText("Tên danh mục")).toHaveValue("Món chính");
    await user.clear(screen.getByLabelText("Mô tả"));
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    await waitFor(() =>
      expect(put).toHaveBeenCalledWith("/categories/{category_id}", {
        path: { category_id: existing.id },
        body: { name: "Món chính", description: null, image_url: null },
      }),
    );
  });

  it("shows the server's field error for a name that is already taken", async () => {
    post.mockRejectedValue(
      new ApiError(422, {
        title: "Validation failed",
        errors: [{ loc: ["body", "name"], msg: "Tên đã dùng", type: "x" }],
      }),
    );
    const user = setup();
    await user.type(screen.getByLabelText("Tên danh mục"), "Món chính");
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    expect(await screen.findByText("Tên đã dùng")).toBeInTheDocument();
  });

  it("explains a 409 conflict in a banner", async () => {
    post.mockRejectedValue(
      new ApiError(409, { title: "Conflict", detail: "A category with this name already exists" }),
    );
    const user = setup();
    await user.type(screen.getByLabelText("Tên danh mục"), "Món chính");
    await user.click(screen.getByRole("button", { name: "Lưu" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "A category with this name already exists",
    );
  });
});
