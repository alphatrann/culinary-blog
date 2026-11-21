import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const serverGet = vi.hoisted(() => vi.fn());
vi.mock("@/lib/api/server", () => ({ serverGet }));

import SearchPage from "./page";

const item = {
  slug: "pho-bo",
  title: "Phở bò Hà Nội",
  category_name: "Món nước",
  prep_time_minutes: 30,
  cook_time_minutes: 150,
  difficulty: 2,
  author_name: "Minh Anh",
  thumbnail_url: null,
  relevance_score: 0.9,
};

function mockApi(items: unknown[]) {
  serverGet.mockImplementation(async (path: string) =>
    path === "/categories"
      ? [{ id: "c1", slug: "mon-nuoc", name: "Món nước" }]
      : {
          items,
          total_count: items.length,
          page: 1,
          page_size: 12,
          total_pages: items.length ? 1 : 0,
        },
  );
}

const render_ = async (sp: Record<string, string>) =>
  render(await SearchPage({ searchParams: Promise.resolve(sp) }));

describe("Search page", () => {
  beforeEach(() => {
    serverGet.mockReset();
  });

  it("prompts without calling the API when q is missing", async () => {
    await render_({});
    expect(screen.getByText("Nhập tên món ăn để bắt đầu tìm.")).toBeInTheDocument();
    expect(serverGet).not.toHaveBeenCalled();
  });

  it("shows a validation hint without calling the API when q is too short", async () => {
    await render_({ q: "p" });
    expect(screen.getByRole("alert")).toHaveTextContent("Nhập ít nhất 2 ký tự");
    expect(serverGet).not.toHaveBeenCalled();
  });

  it("renders results with count and filters, sending q and filters to the API", async () => {
    mockApi([item]);
    await render_({ q: " pho ", difficulty: "easy" });
    expect(screen.getByRole("heading", { name: "Kết quả cho “pho”" })).toBeInTheDocument();
    expect(screen.getByText("Tìm thấy 1 công thức")).toBeInTheDocument();
    expect(screen.getByText("Phở bò Hà Nội")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Bỏ lọc Độ khó: Dễ" })).toBeInTheDocument();
    expect(serverGet).toHaveBeenCalledWith(
      "/recipes/search",
      expect.objectContaining({
        query: expect.objectContaining({ q: "pho", difficulty: "easy", page_size: 12 }),
      }),
    );
  });

  it("shows an empty state when nothing matches", async () => {
    mockApi([]);
    await render_({ q: "xyz" });
    expect(screen.getByText("Chưa tìm thấy công thức nào cho “xyz”")).toBeInTheDocument();
  });

  it("shows an error state when the search request fails", async () => {
    serverGet.mockImplementation((path: string) =>
      path === "/categories" ? [] : Promise.reject(new Error("boom")),
    );
    await render_({ q: "pho" });
    expect(screen.getByText("Không tải được danh sách công thức")).toBeInTheDocument();
  });
});
