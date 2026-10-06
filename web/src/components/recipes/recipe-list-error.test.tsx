import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiError } from "@/lib/api";
import { RecipeListError } from "./recipe-list-error";

describe("RecipeListError", () => {
  it("shows the problem detail and a retry link", () => {
    const err = new ApiError(500, { title: "Server", detail: "Máy chủ bận" }, "abc");
    render(<RecipeListError error={err} retryHref="/recipes?page=2" clearHref="/recipes" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Máy chủ bận");
    expect(screen.getByRole("link", { name: "Thử lại" })).toHaveAttribute(
      "href",
      "/recipes?page=2",
    );
    expect(screen.getByText(/abc/)).toBeInTheDocument();
  });

  it("offers clearing filters on 422", () => {
    const err = new ApiError(422, { title: "Invalid" });
    render(<RecipeListError error={err} retryHref="/recipes?x" clearHref="/recipes" />);
    expect(screen.getByRole("link", { name: "Xóa bộ lọc" })).toHaveAttribute("href", "/recipes");
  });
});
