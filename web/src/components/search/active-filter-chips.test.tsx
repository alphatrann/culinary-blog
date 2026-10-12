import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActiveFilterChips } from "./active-filter-chips";

const cat = "123e4567-e89b-12d3-a456-426614174000";

describe("ActiveFilterChips", () => {
  it("renders nothing without filters", () => {
    const { container } = render(<ActiveFilterChips basePath="/search" q="pho" filters={{}} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders a chip per filter that removes only that filter and keeps q", () => {
    render(
      <ActiveFilterChips
        basePath="/search"
        q="pho"
        filters={{ category_id: cat, difficulty: "easy", max_cook_time: 30 }}
        categories={[{ id: cat, name: "Món nước" }]}
      />,
    );
    expect(screen.getByRole("list", { name: "Bộ lọc đang áp dụng" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Bỏ lọc Độ khó: Dễ" })).toHaveAttribute(
      "href",
      `/search?q=pho&category_id=${cat}&max_cook_time=30`,
    );
    expect(screen.getByRole("link", { name: "Bỏ lọc Danh mục: Món nước" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Bỏ lọc Thời gian/ })).toBeInTheDocument();
  });
});
