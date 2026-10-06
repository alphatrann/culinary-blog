import type { RecipeCardData } from "@/components/recipes/recipe-card";
import { difficultyLabel, formatMinutes } from "@/lib/labels";

type RecipeSummary = {
  slug: string;
  title: string;
  category_name?: string | null;
  author_name?: string | null;
  thumbnail_url?: string | null;
  prep_time_minutes?: number | null;
  cook_time_minutes: number;
  difficulty: number | string;
};

/** Maps an API recipe summary to the props `RecipeCard` expects. */
export function toCardData(r: RecipeSummary): RecipeCardData {
  return {
    slug: r.slug,
    title: r.title,
    category: r.category_name ?? undefined,
    thumbnailUrl: r.thumbnail_url,
    time: formatMinutes((r.prep_time_minutes ?? 0) + r.cook_time_minutes),
    difficulty: difficultyLabel(r.difficulty as never),
    author: r.author_name ?? undefined,
  };
}
