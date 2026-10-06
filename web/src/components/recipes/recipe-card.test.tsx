import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RecipeCard, type RecipeCardData } from "./recipe-card";

const recipe: RecipeCardData = {
  slug: "pho-bo",
  title: "Phở bò",
  category: "Món nước",
  time: "2 giờ",
  difficulty: "Trung bình",
  author: "An",
};

describe("RecipeCard", () => {
  it("links to the recipe detail page and shows its metadata", () => {
    render(<RecipeCard recipe={recipe} />);

    expect(screen.getByRole("link")).toHaveAttribute("href", "/recipes/pho-bo");
    expect(screen.getByText("Phở bò")).toBeInTheDocument();
    expect(screen.getByText("2 giờ")).toBeInTheDocument();
    expect(screen.getByText("Trung bình")).toBeInTheDocument();
  });
});
