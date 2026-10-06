import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Breadcrumb } from "./breadcrumb";
import { IngredientChecklist, formatQuantity } from "./ingredient-checklist";
import { RecipeGallery } from "./recipe-gallery";
import { initials } from "./recipe-header";
import { RecipeNutrition } from "./recipe-nutrition";
import { RecipeSteps } from "./recipe-steps";

const ing = (
  id: string,
  name: string,
  order: number,
  quantity: number | null,
  unit: string | null,
) => ({
  id,
  name,
  order_index: order,
  quantity,
  unit,
  notes: null,
});

describe("IngredientChecklist", () => {
  it("lists ingredients in order and toggles the checkbox", () => {
    render(
      <IngredientChecklist
        ingredients={[ing("b", "Hành tây", 2, 2, "củ"), ing("a", "Xương bò", 1, 1.5, "kg")]}
      />,
    );
    const boxes = screen.getAllByRole("checkbox");
    expect(boxes).toHaveLength(2);
    expect(screen.getAllByRole("listitem")[0]).toHaveTextContent("Xương bò");
    expect(screen.getByText("1,5 kg")).toBeInTheDocument();

    fireEvent.click(boxes[0]);
    expect(boxes[0]).toBeChecked();
    fireEvent.click(boxes[0]);
    expect(boxes[0]).not.toBeChecked();
  });

  it("formats quantity without a unit or without a quantity", () => {
    expect(formatQuantity({ quantity: 3, unit: null })).toBe("3");
    expect(formatQuantity({ quantity: null, unit: "vừa ăn" })).toBe("vừa ăn");
  });
});

describe("RecipeNutrition", () => {
  it("renders nothing when no value is present", () => {
    const { container } = render(<RecipeNutrition nutrition={{ calories: null }} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("shows only the values that exist", () => {
    render(<RecipeNutrition nutrition={{ calories: 520, protein: 32 }} />);
    expect(screen.getByText("Năng lượng")).toBeInTheDocument();
    expect(screen.getByText("520 kcal")).toBeInTheDocument();
    expect(screen.queryByText("Chất béo")).not.toBeInTheDocument();
  });
});

describe("RecipeSteps", () => {
  it("orders steps by step number", () => {
    const step = (n: number, title: string) => ({
      id: String(n),
      step_number: n,
      title,
      description: `Mô tả ${n}`,
      duration_minutes: null,
      image_url: null,
    });
    render(<RecipeSteps steps={[step(2, "Ninh"), step(1, "Chần")]} />);
    const items = screen.getAllByRole("listitem");
    expect(items[0]).toHaveTextContent("Chần");
    expect(items[1]).toHaveTextContent("Ninh");
  });
});

describe("RecipeGallery", () => {
  it("shows a placeholder when the recipe has no image yet", () => {
    render(<RecipeGallery images={[]} title="Phở bò" slug="pho-bo" />);
    expect(screen.getByText("Ảnh món ăn đang được cập nhật")).toBeInTheDocument();
  });
});

describe("Breadcrumb", () => {
  it("marks the last crumb as the current page", () => {
    render(<Breadcrumb items={[{ label: "Trang chủ", href: "/" }, { label: "Phở bò" }]} />);
    expect(screen.getByRole("navigation", { name: "Breadcrumb" })).toBeInTheDocument();
    expect(screen.getByText("Phở bò")).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Trang chủ" })).toHaveAttribute("href", "/");
  });
});

describe("initials", () => {
  it("uses first and last word", () => {
    expect(initials("Minh Anh")).toBe("MA");
    expect(initials("Nguyễn Thị Thu Hà")).toBe("NH");
    expect(initials("Lan")).toBe("L");
  });
});
