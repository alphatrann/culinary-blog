import type { components } from "@/lib/api/schema";
import type { RecipeCardData } from "@/components/recipes/recipe-card";
import { difficultyLabel, formatMinutes } from "@/lib/labels";

export type RecipeSummary = components["schemas"]["RecipeSummaryOut"];

/** API list item → props for `RecipeCard`; the time shown is prep + cook. */
export function toRecipeCardData(recipe: RecipeSummary): RecipeCardData {
  return {
    slug: recipe.slug,
    title: recipe.title,
    category: recipe.category_name,
    thumbnailUrl: recipe.thumbnail_url,
    time: formatMinutes(recipe.prep_time_minutes + recipe.cook_time_minutes),
    difficulty: difficultyLabel(recipe.difficulty as number),
    author: recipe.author_name,
  };
}
