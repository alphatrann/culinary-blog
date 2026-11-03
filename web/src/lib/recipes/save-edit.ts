import type { api } from "@/lib/api";
import { type EditState, formChildren, toUpdatePayload } from "./edit";
import { type Op, planChildOps } from "./diff";
import type { RecipeFormValues } from "./schemas";

export interface SaveEditInput {
  api: typeof api;
  recipeId: string;
  /** Mutated as each call succeeds, so a retry after a partial failure only sends what is still outstanding. */
  state: EditState;
  values: RecipeFormValues;
  /** Called with the server id of each newly created child, so the form row can remember it. */
  onCreated: (list: "ingredients" | "steps", rowIndex: number, id: string) => void;
}

/**
 * Saves a recipe edit: the recipe's own fields first (guarded by `If-Match`), then the ingredient and step changes.
 * A 409 on the first call means nothing changed on the server, so the caller can offer a reload.
 * Any later failure leaves `state` describing exactly what was saved.
 */
export async function saveRecipeEdit({
  api,
  recipeId,
  state,
  values,
  onCreated,
}: SaveEditInput): Promise<void> {
  const recipe = await api.put("/recipes/{recipe_id}", {
    path: { recipe_id: recipeId },
    rowVersion: state.rowVersion,
    body: toUpdatePayload(values),
  });
  state.rowVersion = recipe.row_version;

  const children = formChildren(values);
  for (const op of planChildOps(state.ingredients, children.ingredients, { ordered: false })) {
    await applyIngredientOp(api, recipeId, state, op, onCreated);
  }
  for (const op of planChildOps(state.steps, children.steps, { ordered: true })) {
    await applyStepOp(api, recipeId, state, op, onCreated);
  }
}

async function applyIngredientOp(
  client: typeof api,
  recipeId: string,
  state: EditState,
  op: Op<EditState["ingredients"][number]["payload"]>,
  onCreated: SaveEditInput["onCreated"],
): Promise<void> {
  if (op.kind === "delete") {
    await client.delete("/recipes/{recipe_id}/ingredients/{ingredient_id}", {
      path: { recipe_id: recipeId, ingredient_id: op.id },
    });
    state.ingredients = state.ingredients.filter((i) => i.id !== op.id);
  } else if (op.kind === "update") {
    await client.put("/recipes/{recipe_id}/ingredients/{ingredient_id}", {
      path: { recipe_id: recipeId, ingredient_id: op.id },
      body: op.payload,
    });
    state.ingredients = state.ingredients.map((i) =>
      i.id === op.id ? { id: i.id, payload: op.payload } : i,
    );
  } else {
    const created = await client.post("/recipes/{recipe_id}/ingredients", {
      path: { recipe_id: recipeId },
      body: op.payload,
    });
    state.ingredients.push({ id: created.id, payload: op.payload });
    onCreated("ingredients", op.rowIndex, created.id);
  }
}

async function applyStepOp(
  client: typeof api,
  recipeId: string,
  state: EditState,
  op: Op<EditState["steps"][number]["payload"]>,
  onCreated: SaveEditInput["onCreated"],
): Promise<void> {
  if (op.kind === "delete") {
    await client.delete("/recipes/{recipe_id}/steps/{step_id}", {
      path: { recipe_id: recipeId, step_id: op.id },
    });
    state.steps = state.steps.filter((s) => s.id !== op.id);
  } else if (op.kind === "update") {
    await client.put("/recipes/{recipe_id}/steps/{step_id}", {
      path: { recipe_id: recipeId, step_id: op.id },
      body: op.payload,
    });
    state.steps = state.steps.map((s) => (s.id === op.id ? { id: s.id, payload: op.payload } : s));
  } else {
    const created = await client.post("/recipes/{recipe_id}/steps", {
      path: { recipe_id: recipeId },
      body: op.payload,
    });
    state.steps.push({ id: created.id, payload: op.payload });
    onCreated("steps", op.rowIndex, created.id);
  }
}
