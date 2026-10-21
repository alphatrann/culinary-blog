import type { RequestBody, ResponseBody } from "@/lib/api";
import { deriveStepTitle, type RecipeFormValues, toCreatePayload } from "./schemas";

export type RecipeDetail = ResponseBody<"/recipes/{recipe_id}", "get">;

/** Mirrors `RecipeStatus.PUBLISHED` in src/culinary_blog/recipes/enums.py (the API sends the integer). */
export const PUBLISHED_STATUS = 1;
export type RecipeUpdatePayload = RequestBody<"/recipes/{recipe_id}", "put">;

export interface IngredientPayload {
  name: string;
  quantity: number | null;
  unit: string | null;
  order_index: number;
}

export interface StepPayload {
  title: string;
  description: string;
}

/** The last state the server confirmed, plus the row version the next recipe PUT must send. */
export interface EditState {
  rowVersion: number;
  ingredients: { id: string; payload: IngredientPayload }[];
  steps: { id: string; payload: StepPayload }[];
}

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
      .map((i) => ({ id: i.id, name: i.name, quantity: text(i.quantity), unit: text(i.unit) })),
    steps: [...recipe.steps]
      .sort((a, b) => a.step_number - b.step_number)
      // A step is one textarea whose first line becomes the title on save, so the description is the text.
      .map((s) => ({ id: s.id, text: s.description })),
    nutrition: {
      calories: text(nutrition?.calories),
      protein: text(nutrition?.protein),
      fat: text(nutrition?.fat),
      carbohydrates: text(nutrition?.carbohydrates),
    },
  };
}

/** The recipe's own fields for `PUT /recipes/{id}`; children are synced separately. */
export function toUpdatePayload(values: RecipeFormValues): RecipeUpdatePayload {
  const payload = toCreatePayload(values);
  return {
    title: payload.title,
    description: payload.description,
    category_id: payload.category_id,
    difficulty: payload.difficulty,
    prep_time_minutes: payload.prep_time_minutes,
    cook_time_minutes: payload.cook_time_minutes,
    servings: payload.servings,
    nutrition: payload.nutrition,
  };
}

/** What the server holds for the children, in the shape the diff compares. */
export function editStateFromRecipe(recipe: RecipeDetail): EditState {
  return {
    rowVersion: recipe.row_version,
    ingredients: [...recipe.ingredients]
      .sort((a, b) => a.order_index - b.order_index)
      .map((i) => ({
        id: i.id,
        payload: {
          name: i.name,
          quantity: i.quantity ?? null,
          unit: i.unit ?? null,
          order_index: i.order_index,
        },
      })),
    steps: [...recipe.steps]
      .sort((a, b) => a.step_number - b.step_number)
      .map((s) => ({ id: s.id, payload: { title: s.title, description: s.description } })),
  };
}

/** Payloads derived from the form, in the same shape `editStateFromRecipe` produces. */
export function formChildren(values: RecipeFormValues) {
  const ingredients = values.ingredients.map((i, rowIndex) => ({
    rowIndex,
    id: i.id,
    payload:
      i.name.trim() === ""
        ? null
        : {
            name: i.name.trim(),
            quantity: i.quantity.trim() ? Number(i.quantity.trim().replace(",", ".")) : null,
            unit: i.unit.trim() || null,
            order_index: 0,
          },
  }));
  // order_index counts only the rows that are kept, matching what toCreatePayload sends.
  let position = 0;
  for (const row of ingredients) if (row.payload) row.payload.order_index = position++;

  const steps = values.steps.map((s, rowIndex) => ({
    rowIndex,
    id: s.id,
    payload:
      s.text.trim() === "" ? null : { title: deriveStepTitle(s.text), description: s.text.trim() },
  }));
  return { ingredients, steps };
}
