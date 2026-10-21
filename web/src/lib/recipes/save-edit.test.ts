import { describe, expect, it, vi } from "vitest";
import type { api } from "@/lib/api";
import { ApiError } from "@/lib/api";
import { editStateFromRecipe, toFormValues, type EditState } from "./edit";
import { saveRecipeEdit } from "./save-edit";
import { sampleRecipe } from "./recipe-fixture";
import type { RecipeFormValues } from "./schemas";

const RECIPE_ID = sampleRecipe.id;

function fakeApi(
  overrides: Partial<Record<"put" | "post" | "delete", (...args: unknown[]) => unknown>> = {},
) {
  const calls: string[] = [];
  const record = (name: string, impl?: (...args: unknown[]) => unknown) =>
    vi.fn(async (path: string, options: unknown) => {
      calls.push(`${name} ${path}`);
      if (impl) return impl(path, options);
      return name === "put" && path === "/recipes/{recipe_id}"
        ? { ...sampleRecipe, row_version: 5 }
        : { id: `new-${calls.length}` };
    });
  const client = {
    put: record("put", overrides.put),
    post: record("post", overrides.post),
    delete: record("delete", overrides.delete),
  };
  return { api: client as unknown as typeof api, calls };
}

/** Like the editor: a created child's id is written back into its form row, so the next save sees it as existing. */
function input(values: RecipeFormValues, state: EditState) {
  const onCreated = (list: "ingredients" | "steps", rowIndex: number, id: string) => {
    values[list][rowIndex]!.id = id;
  };
  return { recipeId: RECIPE_ID, state, values, onCreated };
}

describe("saveRecipeEdit", () => {
  it("updates the recipe with If-Match and advances the stored row version", async () => {
    const state = editStateFromRecipe(sampleRecipe);
    const { api: client, calls } = fakeApi();

    await saveRecipeEdit({ ...input(toFormValues(sampleRecipe), state), api: client });

    expect(calls[0]).toBe("put /recipes/{recipe_id}");
    expect(state.rowVersion).toBe(5);
    expect(calls).toHaveLength(1); // nothing changed in the children
  });

  it("sends changed, added and removed children and reports created ids", async () => {
    const state = editStateFromRecipe(sampleRecipe);
    const values = toFormValues(sampleRecipe);
    values.ingredients[1]!.name = "Bánh phở tươi";
    values.ingredients.push({ name: "Hành", quantity: "2", unit: "củ" });
    values.ingredients.splice(0, 1); // drop Thịt bò (i1)
    const { api: client, calls } = fakeApi();
    const onCreated = vi.fn();

    await saveRecipeEdit({ api: client, recipeId: RECIPE_ID, state, values, onCreated });

    expect(calls).toEqual([
      "put /recipes/{recipe_id}",
      "delete /recipes/{recipe_id}/ingredients/{ingredient_id}",
      "put /recipes/{recipe_id}/ingredients/{ingredient_id}",
      "post /recipes/{recipe_id}/ingredients",
    ]);
    // After dropping row 0, the new "Hành" row is at index 1 of the form array.
    expect(onCreated).toHaveBeenCalledWith("ingredients", 1, expect.any(String));
    expect(state.ingredients.map((i) => i.id)).toEqual(["i2", expect.any(String)]);
  });

  it("does not touch children when the recipe PUT is rejected with 409", async () => {
    const state = editStateFromRecipe(sampleRecipe);
    const values = toFormValues(sampleRecipe);
    values.steps.push({ text: "Thêm bước" });
    const conflict = new ApiError(409, { title: "Conflict", detail: "stale" });
    const { api: client, calls } = fakeApi({ put: () => Promise.reject(conflict) });

    await expect(saveRecipeEdit({ ...input(values, state), api: client })).rejects.toBe(conflict);
    expect(calls).toEqual(["put /recipes/{recipe_id}"]);
    expect(state.rowVersion).toBe(sampleRecipe.row_version);
  });

  it("retries only the outstanding calls after a partial failure", async () => {
    const state = editStateFromRecipe(sampleRecipe);
    const values = toFormValues(sampleRecipe);
    values.ingredients.push({ name: "Hành", quantity: "2", unit: "củ" });
    values.steps.push({ text: "Thêm bước" });

    let failStep = true;
    const { api: client, calls } = fakeApi({
      post: (path) => {
        if (String(path).includes("/steps") && failStep) {
          return Promise.reject(new ApiError(500, { title: "Server Error" }));
        }
        return Promise.resolve({ id: `created-${String(path).split("/").pop()}` });
      },
    });

    await expect(saveRecipeEdit({ ...input(values, state), api: client })).rejects.toThrow();
    expect(calls.filter((c) => c.startsWith("post"))).toEqual([
      "post /recipes/{recipe_id}/ingredients",
      "post /recipes/{recipe_id}/steps",
    ]);
    expect(state.ingredients.some((i) => i.id === "created-ingredients")).toBe(true);

    calls.length = 0;
    failStep = false;
    await saveRecipeEdit({ ...input(values, state), api: client });

    // The ingredient is now known to the server, so only the step is sent again.
    expect(calls).toEqual(["put /recipes/{recipe_id}", "post /recipes/{recipe_id}/steps"]);
  });
});
