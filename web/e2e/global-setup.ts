import { request } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

/** Written by global setup and read by specs that need an existing published recipe. */
export const STATE_FILE = join(__dirname, ".state.json");

export interface E2EState {
  recipeTitle: string;
  recipeSlug: string;
  /** A token only this run's recipe contains, so searching for it returns just that recipe. */
  searchToken: string;
}

/**
 * Creates one published recipe through the public API so browse specs have something to find.
 * Needs at least one category in the database (seed it with scripts/seed or the e2e SQL fixture).
 */
export default async function globalSetup(): Promise<void> {
  // No default on purpose: a guessed port can point at another project's database.
  const apiBase = process.env.E2E_API_URL;
  if (!apiBase) throw new Error("Set E2E_API_URL to the API this run may write test data to.");
  const api = await request.newContext({ baseURL: apiBase });
  const stamp = Date.now();
  const email = `e2e-owner-${stamp}@example.com`;
  const password = "E2e-pass-2026!";

  const registered = await api.post("/api/v1/auth/register", {
    data: { email, password, display_name: "E2E Owner" },
  });
  if (!registered.ok())
    throw new Error(`register failed: ${registered.status()} ${await registered.text()}`);

  const categories = await (await api.get("/api/v1/categories")).json();
  if (!Array.isArray(categories) || categories.length === 0) {
    throw new Error(
      "No categories found. Seed the database before running e2e (see scripts/seed).",
    );
  }

  // Letters only: the full-text parser splits tokens that mix letters and digits.
  const searchToken = `zq${stamp.toString(36).replace(/[0-9]/g, (d) => String.fromCharCode(97 + Number(d)))}`;
  const title = `Canh chua ${searchToken}`;
  const created = await api.post("/api/v1/recipes", {
    data: {
      title,
      description: "Món canh chua cho bài kiểm thử đầu cuối.",
      category_id: categories[0].id,
      difficulty: 1,
      prep_time_minutes: 10,
      cook_time_minutes: 20,
      servings: 2,
      ingredients: [{ name: "Cá lóc", quantity: 300, unit: "g", order_index: 0 }],
      steps: [{ title: "Nấu nước dùng", description: "Nấu nước dùng với me." }],
      nutrition: null,
    },
  });
  if (!created.ok())
    throw new Error(`create recipe failed: ${created.status()} ${await created.text()}`);
  const recipe = await created.json();

  const published = await api.patch(`/api/v1/recipes/${recipe.id}/publish`);
  if (!published.ok())
    throw new Error(`publish failed: ${published.status()} ${await published.text()}`);

  const state: E2EState = { recipeTitle: title, recipeSlug: recipe.slug, searchToken };
  mkdirSync(__dirname, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  await api.dispose();
}
