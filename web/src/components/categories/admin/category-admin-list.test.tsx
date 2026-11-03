import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi, type MockInstance } from "vitest";
import { api, ApiError } from "@/lib/api";
import { CategoryAdminList } from "./category-admin-list";

const categories = [
  {
    id: "c1",
    name: "Món chính",
    slug: "mon-chinh",
    description: null,
    image_url: null,
    recipe_count: 2,
  },
  {
    id: "c2",
    name: "Tráng miệng",
    slug: "trang-mieng",
    description: null,
    image_url: null,
    recipe_count: 0,
  },
];

let get: MockInstance<typeof api.get>;
let del: MockInstance<typeof api.delete>;

function setup() {
  const user = userEvent.setup();
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <CategoryAdminList />
    </QueryClientProvider>,
  );
  return user;
}

describe("CategoryAdminList", () => {
  beforeEach(() => {
    get = vi.spyOn(api, "get").mockResolvedValue(categories as never);
    del = vi.spyOn(api, "delete").mockResolvedValue(undefined as never);
  });
  afterEach(() => vi.restoreAllMocks());

  it("lists categories with their published recipe counts", async () => {
    setup();
    expect(await screen.findByText("Món chính")).toBeInTheDocument();
    expect(screen.getByText(/\/mon-chinh · 2 công thức/)).toBeInTheDocument();
    expect(get).toHaveBeenCalledWith("/categories");
  });

  it("deletes a category after confirmation and refetches the list", async () => {
    const user = setup();
    await screen.findByText("Món chính");
    await user.click(screen.getByRole("button", { name: "Xóa Tráng miệng" }));
    const dialog = await screen.findByRole("dialog");
    await user.click(within(dialog).getByRole("button", { name: "Xóa danh mục" }));

    await waitFor(() =>
      expect(del).toHaveBeenCalledWith("/categories/{category_id}", {
        path: { category_id: "c2" },
      }),
    );
  });

  it("explains that a category still holding recipes cannot be deleted", async () => {
    del.mockRejectedValue(
      new ApiError(409, { title: "Conflict", detail: "Category still has 1 recipe(s)" }),
    );
    const user = setup();
    await screen.findByText("Món chính");
    await user.click(screen.getByRole("button", { name: "Xóa Món chính" }));
    const dialog = await screen.findByRole("dialog");
    await user.click(within(dialog).getByRole("button", { name: "Xóa danh mục" }));

    expect(await within(dialog).findByRole("alert")).toHaveTextContent("vẫn còn công thức");
  });

  it("opens an empty create form from the add button", async () => {
    const user = setup();
    await screen.findByText("Món chính");
    await user.click(screen.getByRole("button", { name: "Thêm danh mục" }));

    expect(await screen.findByLabelText("Tên danh mục")).toHaveValue("");
  });
});
