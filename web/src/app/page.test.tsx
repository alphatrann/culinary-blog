import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const serverGet = vi.hoisted(() => vi.fn());
vi.mock("@/lib/api/server", () => ({ serverGet }));

import Home from "./page";

const item = {
  slug: "pho-bo",
  title: "Phở bò Hà Nội",
  description: "Nước dùng trong.",
  category_name: "Món nước",
  prep_time_minutes: 30,
  cook_time_minutes: 150,
  difficulty: 2,
  author_name: "Minh Anh",
  thumbnail_url: null,
};

function mockApi(items: unknown[], totalCount = items.length) {
  serverGet.mockImplementation(async (path: string) =>
    path === "/categories"
      ? [{ slug: "mon-nuoc", name: "Món nước" }]
      : { items, total_count: totalCount, page: 1, page_size: 8, total_pages: 1 },
  );
}

describe("Home page", () => {
  beforeEach(() => {
    serverGet.mockReset();
  });

  it("renders the newest recipe as featured and in the list", async () => {
    mockApi([item]);
    render(await Home());
    expect(screen.getByRole("heading", { name: "Công thức mới nhất" })).toBeInTheDocument();
    expect(screen.getByLabelText("Món nổi bật: Phở bò Hà Nội")).toBeInTheDocument();
    expect(screen.getByText("Hiển thị 1 công thức")).toBeInTheDocument();
    expect(screen.getByRole("search", { name: "Bộ lọc công thức" })).toHaveAttribute(
      "action",
      "/recipes",
    );
  });

  it("shows an empty state when there are no recipes", async () => {
    mockApi([]);
    render(await Home());
    expect(screen.getByText("Chưa có công thức nào")).toBeInTheDocument();
  });

  it("shows an error alert, not a crash, when the API is unavailable", async () => {
    serverGet.mockRejectedValue(new Error("down"));
    render(await Home());
    expect(screen.getByRole("alert")).toHaveTextContent("Không thể tải công thức");
    expect(screen.getByRole("search", { name: "Tìm công thức" })).toBeInTheDocument();
  });
});
