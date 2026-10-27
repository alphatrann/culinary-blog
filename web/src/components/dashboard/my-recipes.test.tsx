import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { MyRecipes } from "./my-recipes";

const get = vi.fn();
vi.mock("@/lib/api", async (orig) => ({
  ...(await orig<typeof import("@/lib/api")>()),
  api: { get: (...a: unknown[]) => get(...a) },
}));

const recipe = (over: Record<string, unknown>) => ({
  id: "r1",
  slug: "pho-bo",
  title: "Phở bò",
  category_name: "Món chính",
  updated_at: "2026-10-01T10:00:00Z",
  status: 0,
  ...over,
});

const page = (items: unknown[], extra: Record<string, unknown> = {}) => ({
  items,
  total_count: items.length,
  page: 1,
  page_size: 10,
  total_pages: 1,
  has_next_page: false,
  has_previous_page: false,
  status_counts: { draft: 2, published: 1, archived: 0 },
  ...extra,
});

function renderList(props: Partial<React.ComponentProps<typeof MyRecipes>> = {}) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MyRecipes basePath="/dashboard/recipes" tab="all" page={1} {...props} />
    </QueryClientProvider>,
  );
}

describe("MyRecipes", () => {
  beforeEach(() => {
    // Braces matter: a returned value from beforeEach is treated as a teardown and would re-run the mock.
    get.mockReset();
  });

  it("shows tab counts from the response and marks the active tab", async () => {
    get.mockResolvedValue(page([recipe({})]));
    renderList({ tab: "draft" });

    const nav = await screen.findByRole("navigation", { name: "Lọc theo trạng thái" });
    // Counts appear once the list has loaded; wait for them before reading the tabs.
    await within(nav).findByRole("link", { name: /Tất cả\s*3/ });
    expect(within(nav).getByRole("link", { name: /Tất cả/ })).toHaveTextContent("3");
    expect(within(nav).getByRole("link", { name: /Đã xuất bản/ })).toHaveTextContent("1");
    expect(within(nav).getByRole("link", { name: /Bản nháp/ })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it("requests only the author's recipes, with the tab's status", async () => {
    get.mockResolvedValue(page([]));
    renderList({ tab: "published", page: 2 });

    await screen.findByText("Không có công thức trong mục này");
    expect(get).toHaveBeenCalledWith("/recipes", {
      query: { author_id: "me", status: "published", page: 2, page_size: 10 },
    });
  });

  it("links each row to the edit page and published rows to the public page", async () => {
    get.mockResolvedValue(
      page([
        recipe({ id: "a", title: "Bản nháp", status: 0 }),
        recipe({ id: "b", slug: "pho", title: "Đã đăng", status: 1 }),
      ]),
    );
    renderList();

    const edits = await screen.findAllByRole("link", { name: "Sửa" });
    expect(edits.map((a) => a.getAttribute("href"))).toEqual([
      "/dashboard/recipes/a/edit",
      "/dashboard/recipes/b/edit",
    ]);
    // Title links share their text with the tab labels, so match them by href.
    const titleLinks = screen
      .getAllByRole("link")
      .filter((a) => a.getAttribute("href")?.endsWith("/edit") && a.textContent !== "Sửa");
    expect(titleLinks.map((a) => a.textContent)).toEqual(["Bản nháp", "Đã đăng"]);
    expect(screen.getAllByRole("link", { name: "Xem" })).toHaveLength(1);
    expect(screen.getByRole("link", { name: "Xem" })).toHaveAttribute("href", "/recipes/pho");
  });

  it("shows an empty state with a way to write a recipe", async () => {
    get.mockResolvedValue(page([], { status_counts: { draft: 0, published: 0, archived: 0 } }));
    renderList();

    expect(await screen.findByText("Bạn chưa có công thức nào")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Viết công thức mới" })).toHaveAttribute(
      "href",
      "/dashboard/recipes/new",
    );
  });

  it("shows an error state when the list fails to load", async () => {
    get.mockImplementation(async () => {
      throw new ApiError(500, { title: "Server Error" });
    });
    renderList();

    expect(await screen.findByText("Không tải được công thức")).toBeInTheDocument();
  });

  it("paginates with links that keep the tab", async () => {
    get.mockResolvedValue(page([recipe({})], { total_pages: 3, page: 1 }));
    renderList({ tab: "draft" });

    const pager = await screen.findByRole("navigation", { name: "Phân trang" });
    expect(within(pager).getByRole("link", { name: "2" })).toHaveAttribute(
      "href",
      "/dashboard/recipes?status=draft&page=2",
    );
  });
});
