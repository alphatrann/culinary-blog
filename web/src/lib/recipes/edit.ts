import type { RequestBody, ResponseBody } from "@/lib/api";
import { type RecipeFormValues, toCreatePayload } from "./schemas";

export type RecipeDetail = ResponseBody<"/recipes/{recipe_id}", "get">;

/** Mirrors `RecipeStatus.PUBLISHED` in src/culinary_blog/recipes/enums.py (the API sends the integer). */
export const PUBLISHED_STATUS = 1;
export type RecipeUpdatePayload = RequestBody<"/recipes/{recipe_id}", "put">;

const text = (v: number | string | null | undefined) =>
  v === null || v === undefined ? "" : String(v);

export function toFormValues(recipe: RecipeDetail): RecipeFormValues {
  const nutrition = recipe.nutrition;
  return {
    title: recipe.title,
    description: recipe.description,
    category_id: recipe.category_id,
    difficulty: String(recipe.difficulty) as RecipeFormValues["difficulty"],
    prep_time_minutes: String(recipe.prep_time_minutes),
    cook_time_minutes: String(recipe.cook_time_minutes),
    servings: String(recipe.servings),
    ingredients: [...recipe.ingredients]
      .sort((a, b) => a.order_index - b.order_index)
      .map((i) => ({ name: i.name, quantity: text(i.quantity), unit: text(i.unit) })),
    steps: [...recipe.steps]
      .sort((a, b) => a.step_number - b.step_number)
      // A step is one textarea whose first line becomes the title on save, so the description is the text.
      .map((s) => ({ text: s.description })),
    nutrition: {
      calories: text(nutrition?.calories),
      protein: text(nutrition?.protein),
      fat: text(nutrition?.fat),
      carbohydrates: text(nutrition?.carbohydrates),
    },
  };
}

/** Full atomic payload for `PUT /recipes/{id}` (recipe fields, nutrition, ingredients, and steps). */
export function toUpdatePayload(values: RecipeFormValues): RecipeUpdatePayload {
  return toCreatePayload(values);
}
