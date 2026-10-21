import { describe, expect, it } from "vitest";
import { editStateFromRecipe, formChildren, toFormValues, toUpdatePayload } from "./edit";
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
  it("maps scalars to strings and keeps server ids on child rows, ordered by position", () => {
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
      { id: "i1", name: "Thịt bò", quantity: "", unit: "" },
      { id: "i2", name: "Bánh phở", quantity: "500", unit: "g" },
    ]);
    expect(values.steps).toEqual([
      { id: "s1", text: "Ninh xương\nNinh xương 3 giờ." },
      { id: "s2", text: "Ăn khi nóng." },
    ]);
  });
});

describe("toUpdatePayload", () => {
  it("sends only the recipe's own fields", () => {
    const payload = toUpdatePayload({
      ...emptyRecipeForm,
      title: "Phở bò Hà Nội",
      description: "Món phở.",
      category_id: "22222222-2222-4222-8222-222222222222",
      prep_time_minutes: "30",
      cook_time_minutes: "180",
      servings: "4",
      ingredients: [{ name: "Thịt bò", quantity: "", unit: "" }],
      steps: [{ text: "Ninh" }],
    });

    expect(Object.keys(payload).sort()).toEqual(
      [
        "category_id",
        "cook_time_minutes",
        "description",
        "difficulty",
        "nutrition",
        "prep_time_minutes",
        "servings",
        "title",
      ].sort(),
    );
  });
});

describe("editStateFromRecipe and formChildren", () => {
  it("builds the same payload shapes from the server and from the form, so an unchanged recipe diffs empty", () => {
    const state = editStateFromRecipe(sampleRecipe);
    const children = formChildren(toFormValues(sampleRecipe));

    const serverIngredients = state.ingredients.map((i) => JSON.stringify(i.payload));
    const formIngredients = children.ingredients.map((i) => JSON.stringify(i.payload));
    expect(formIngredients).toEqual(serverIngredients);

    const serverSteps = state.steps.map((s) => JSON.stringify(s.payload));
    const formSteps = children.steps.map((s) => JSON.stringify(s.payload));
    expect(formSteps).toEqual(serverSteps);
  });

  it("drops blank rows and renumbers ingredient order_index over the kept rows only", () => {
    const children = formChildren({
      ...toFormValues(sampleRecipe),
      ingredients: [
        { id: "i1", name: "", quantity: "", unit: "" },
        { name: "Hành", quantity: "2", unit: "củ" },
      ],
    });

    expect(children.ingredients[0]!.payload).toBeNull();
    expect(children.ingredients[1]!.payload).toEqual({
      name: "Hành",
      quantity: 2,
      unit: "củ",
      order_index: 0,
    });
  });
});
