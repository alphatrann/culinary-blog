import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RecipeGrid } from "./recipe-grid";

describe("RecipeGrid", () => {
  it("shows the empty state with a custom title", () => {
    render(<RecipeGrid recipes={[]} emptyTitle="Không tìm thấy công thức phù hợp" />);
    expect(screen.getByText("Không tìm thấy công thức phù hợp")).toBeInTheDocument();
  });

  it("renders a card per recipe", () => {
    render(
      <RecipeGrid recipes={[{ slug: "a", title: "Phở", time: "30 phút", difficulty: "Dễ" }]} />,
    );
    expect(screen.getByRole("link", { name: /Phở/ })).toHaveAttribute("href", "/recipes/a");
  });
});
