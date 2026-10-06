import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RecipeFilterBar } from "./recipe-filter-bar";

describe("RecipeFilterBar", () => {
  it("renders a category select when categories are given", () => {
    render(<RecipeFilterBar basePath="/recipes" categories={[{ id: "1", name: "Món nước" }]} />);
    expect(screen.getByLabelText("Danh mục")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Xóa bộ lọc" })).toBeNull();
  });

  it("omits the category select without categories and shows clear link when filtered", () => {
    render(<RecipeFilterBar basePath="/recipes" categoryId="1" hidden={{ q: "phở" }} />);
    expect(screen.queryByLabelText("Danh mục")).toBeNull();
    expect(screen.getByRole("link", { name: "Xóa bộ lọc" })).toHaveAttribute(
      "href",
      "/recipes?q=ph%E1%BB%9F",
    );
  });
});
