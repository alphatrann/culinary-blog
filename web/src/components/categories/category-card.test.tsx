import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryGrid, type CategoryCardData } from "./category-card";

const category: CategoryCardData = {
  slug: "mon-nuoc",
  name: "Món nước",
  description: "Phở, bún, hủ tiếu và các món có nước dùng.",
  recipeCount: 12,
};

describe("CategoryGrid", () => {
  it("links each card to its category page with name and recipe count", () => {
    render(
      <CategoryGrid
        categories={[category, { ...category, slug: "mon-xao", name: "Món xào", recipeCount: 0 }]}
      />,
    );

    expect(screen.getByRole("link", { name: /Món nước/ })).toHaveAttribute(
      "href",
      "/categories/mon-nuoc",
    );
    expect(screen.getByText("12 công thức")).toBeInTheDocument();
    expect(screen.getByText("0 công thức")).toBeInTheDocument();
  });

  it("omits the description when the category has none", () => {
    render(<CategoryGrid categories={[{ ...category, description: null }]} />);

    expect(screen.queryByText(/nước dùng/)).not.toBeInTheDocument();
  });
});
