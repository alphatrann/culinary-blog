import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { SearchFilterPanel } from "./search-filter-panel";

const categories = [{ id: "c1", name: "Món nước" }];

describe("SearchFilterPanel", () => {
  it("carries q in a hidden field and checks the active options", () => {
    const { container } = render(
      <SearchFilterPanel
        basePath="/search"
        q="pho"
        categories={categories}
        difficulty="easy"
        maxCookTime={30}
      />,
    );
    expect(container.querySelector('input[name="q"]')).toHaveValue("pho");
    expect(screen.getByRole("radio", { name: "Dễ" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "Tối đa 30 phút" })).toBeChecked();
    expect(screen.getAllByRole("radio", { name: "Tất cả" })[0]).toBeChecked();
  });

  it("shows the active count badge and a clear link that keeps q", () => {
    render(
      <SearchFilterPanel
        basePath="/search"
        q="pho"
        categoryId="c1"
        difficulty="hard"
        categories={categories}
      />,
    );
    expect(screen.getByLabelText("2 bộ lọc đang áp dụng")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Xóa bộ lọc" })).toHaveAttribute(
      "href",
      "/search?q=pho",
    );
  });

  it("hides the badge and clear link when nothing is active", () => {
    render(<SearchFilterPanel basePath="/search" q="pho" categories={categories} />);
    expect(screen.queryByLabelText(/bộ lọc đang áp dụng/)).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Xóa bộ lọc" })).not.toBeInTheDocument();
  });

  it("toggles aria-expanded on the Bộ lọc button", async () => {
    render(<SearchFilterPanel basePath="/search" q="pho" />);
    const toggle = screen.getByRole("button", { name: /Bộ lọc/ });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
  });
});
