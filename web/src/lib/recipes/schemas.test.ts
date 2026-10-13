import { describe, expect, it } from "vitest";
import {
  deriveStepTitle,
  emptyRecipeForm,
  isPublishable,
  recipeFormSchema,
  toCreatePayload,
  type RecipeFormValues,
} from "./schemas";

const valid: RecipeFormValues = {
  ...emptyRecipeForm,
  title: "Phở bò Hà Nội",
  description: "Món phở truyền thống.",
  category_id: "7d9b0c3e-2f5a-4c1e-9a7b-1b2c3d4e5f60",
  difficulty: "2",
  prep_time_minutes: "30",
  cook_time_minutes: "180",
  servings: "4",
  ingredients: [
    { name: "Thịt bò", quantity: "500", unit: "g" },
    { name: "", quantity: "", unit: "" },
  ],
  steps: [{ text: "Ninh xương\nTrong 3 giờ." }, { text: "  " }],
};

const messages = (v: RecipeFormValues) =>
  recipeFormSchema.safeParse(v).error?.issues.map((i) => `${i.path.join(".")}: ${i.message}`) ?? [];

describe("recipeFormSchema", () => {
  it("accepts a valid form with blank trailing rows", () => {
    expect(recipeFormSchema.safeParse(valid).success).toBe(true);
  });

  it("enforces title length and forbids angle brackets", () => {
    expect(messages({ ...valid, title: "abcd" })).toContain(
      "title: Tiêu đề cần từ 5 đến 200 ký tự.",
    );
    expect(messages({ ...valid, title: "a".repeat(201) })).toHaveLength(1);
    expect(messages({ ...valid, title: "Món <b>ngon</b>" })[0]).toMatch(/^title:/);
  });

  it("requires positive integers for time and servings", () => {
    const errs = messages({
      ...valid,
      prep_time_minutes: "0",
      cook_time_minutes: "1.5",
      servings: "",
    });
    expect([...new Set(errs.map((e) => e.split(":")[0]))].sort()).toEqual([
      "cook_time_minutes",
      "prep_time_minutes",
      "servings",
    ]);
  });

  it("requires quantity and unit together", () => {
    expect(
      messages({ ...valid, ingredients: [{ name: "Muối", quantity: "2", unit: "" }] }),
    ).toEqual(["ingredients.0.unit: Nhập đơn vị."]);
    expect(
      messages({ ...valid, ingredients: [{ name: "Muối", quantity: "", unit: "g" }] }),
    ).toEqual(["ingredients.0.quantity: Nhập số lượng."]);
  });

  it("rejects negative nutrition and more than 2 decimals", () => {
    const nutrition = { ...valid.nutrition, calories: "-1", fat: "1.234" };
    expect(messages({ ...valid, nutrition }).map((e) => e.split(":")[0])).toEqual([
      "nutrition.calories",
      "nutrition.fat",
    ]);
  });
});

describe("toCreatePayload", () => {
  it("drops blank rows, derives step titles and converts numbers", () => {
    const payload = toCreatePayload(valid);
    expect(payload.difficulty).toBe(2);
    expect(payload.prep_time_minutes).toBe(30);
    expect(payload.ingredients).toEqual([
      { name: "Thịt bò", quantity: 500, unit: "g", order_index: 0 },
    ]);
    expect(payload.steps).toEqual([
      { title: "Ninh xương", description: "Ninh xương\nTrong 3 giờ." },
    ]);
    expect(payload.nutrition).toBeNull();
  });

  it("sends only filled nutrition values, accepting decimal commas", () => {
    const payload = toCreatePayload({
      ...valid,
      nutrition: { ...valid.nutrition, calories: "450", protein: "12,5" },
    });
    expect(payload.nutrition).toEqual({ calories: 450, protein: 12.5 });
  });
});

describe("deriveStepTitle / isPublishable", () => {
  it("truncates long first lines to 200 characters", () => {
    expect(deriveStepTitle("x".repeat(500))).toHaveLength(200);
  });

  it("ignores blank rows in the publish checklist", () => {
    expect(
      isPublishable({
        ingredients: [{ name: " ", quantity: "", unit: "" }],
        steps: [{ text: "a" }],
      }),
    ).toEqual({
      ingredients: false,
      steps: true,
    });
  });
});
