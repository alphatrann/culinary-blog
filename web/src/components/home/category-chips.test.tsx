import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryChips } from "./category-chips";

describe("CategoryChips", () => {
  it("lists all recipes first, then each category", () => {
    render(<CategoryChips categories={[{ slug: "mon-nuoc", name: "Món nước" }]} />);
    expect(screen.getByRole("link", { name: "Tất cả" })).toHaveAttribute("href", "/recipes");
    expect(screen.getByRole("link", { name: "Tất cả" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Món nước" })).toHaveAttribute(
      "href",
      "/categories/mon-nuoc",
    );
  });
});
