import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Hero } from "./hero";

describe("Hero", () => {
  it("submits a GET search to /search?q=", () => {
    render(<Hero />);
    const form = screen.getByRole("search", { name: "Tìm công thức" });
    expect(form).toHaveAttribute("action", "/search");
    expect(form).toHaveAttribute("method", "get");
    const input = screen.getByRole("searchbox");
    expect(input).toHaveAttribute("name", "q");
    expect(input).not.toHaveAttribute("placeholder");
    expect(screen.getByRole("button", { name: "Tìm kiếm" })).toBeInTheDocument();
  });

  it("shows the featured recipe only when there is one", () => {
    const { rerender } = render(<Hero />);
    expect(screen.queryByText("Món nổi bật")).not.toBeInTheDocument();
    rerender(
      <Hero featured={{ slug: "pho-bo", title: "Phở bò", description: "Nước dùng trong." }} />,
    );
    expect(screen.getByRole("link", { name: /Phở bò/ })).toHaveAttribute("href", "/recipes/pho-bo");
  });
});
