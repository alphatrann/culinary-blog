import { describe, expect, it } from "vitest";
import { toFormValues, toUpdatePayload } from "./edit";
import { sampleRecipe } from "./recipe-fixture";
import { deriveStepTitle, emptyRecipeForm } from "./schemas";

describe("step text round trip", () => {
  it("gives the saved description back as the textarea text, whose first line is the title", () => {
    const [first] = toFormValues(sampleRecipe).steps;

    expect(first!.text).toBe("Ninh xương\nNinh xương 3 giờ.");
    expect(deriveStepTitle(first!.text)).toBe("Ninh xương");
  });
});

describe("toFormValues", () => {
  it("maps scalars to strings and orders ingredients and steps by position", () => {
    const values = toFormValues(sampleRecipe);

    expect(values).toMatchObject({
      title: "Phở bò Hà Nội",
      category_id: "22222222-2222-4222-8222-222222222222",
      difficulty: "2",
      prep_time_minutes: "30",
      servings: "4",
      nutrition: { calories: "450", protein: "", fat: "9.5", carbohydrates: "" },
    });
    expect(values.ingredients).toEqual([
      { name: "Thịt bò", quantity: "", unit: "" },
      { name: "Bánh phở", quantity: "500", unit: "g" },
    ]);
    expect(values.steps).toEqual([
      { text: "Ninh xương\nNinh xương 3 giờ." },
      { text: "Ăn khi nóng." },
    ]);
  });
});

describe("toUpdatePayload", () => {
  it("includes recipe fields, nutrition, ingredients, and steps for an atomic PUT", () => {
    const payload = toUpdatePayload({
      ...emptyRecipeForm,
      title: "Phở bò Hà Nội",
      description: "Món phở.",
      category_id: "22222222-2222-4222-8222-222222222222",
      prep_time_minutes: "30",
      cook_time_minutes: "180",
      servings: "4",
      ingredients: [
        { name: "", quantity: "", unit: "" },
        { name: "Thịt bò", quantity: "500", unit: "g" },
      ],
      steps: [{ text: "" }, { text: "Ninh xương\nNinh 3 giờ" }],
    });

    expect(payload.ingredients).toEqual([
      { name: "Thịt bò", quantity: 500, unit: "g", order_index: 0 },
    ]);
    expect(payload.steps).toEqual([{ title: "Ninh xương", description: "Ninh xương\nNinh 3 giờ" }]);
  });
});
