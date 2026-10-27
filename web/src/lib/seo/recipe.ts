import type { Metadata } from "next";
import type { components } from "@/lib/api/schema";

type Recipe = components["schemas"]["RecipeDetailOut"];

/** RecipeStatus IntEnum value for published (see recipes/enums.py). */
const PUBLISHED = 1;
const SITE_NAME = "Culinary Blog";
const TITLE_MAX = 60;
const DESCRIPTION_MAX = 160;

function truncate(text: string, max: number): string {
  return text.length <= max ? text : `${text.slice(0, max - 1).trimEnd()}…`;
}

/** ISO-8601 duration for whole minutes, e.g. 90 -> "PT90M". */
function isoMinutes(minutes: number): string {
  return `PT${minutes}M`;
}

export function buildRecipeMetadata(recipe: Recipe, siteUrl: string): Metadata {
  const suffix = ` · ${SITE_NAME}`;
  const title = truncate(recipe.title, TITLE_MAX - suffix.length) + suffix;
  const description = truncate(recipe.description, DESCRIPTION_MAX);
  const url = `${siteUrl}/recipes/${recipe.slug}`;
  const primary = recipe.images.find((image) => image.is_primary);
  const images = primary ? [primary.original_url] : undefined;
  const published = recipe.status === PUBLISHED;

  return {
    title,
    description,
    alternates: { canonical: url },
    robots: { index: published, follow: published },
    openGraph: { title, description, url, type: "article", images },
    twitter: { card: "summary_large_image", title, description, images },
  };
}

export function buildRecipeJsonLd(recipe: Recipe, siteUrl: string): Record<string, unknown> {
  const images = recipe.images.map((image) => image.original_url);
  const totalMinutes = recipe.prep_time_minutes + recipe.cook_time_minutes;
  const nutrition = recipe.nutrition;
  const hasNutrition = Object.values(nutrition).some((value) => value != null);

  return {
    "@context": "https://schema.org",
    "@type": "Recipe",
    name: recipe.title,
    description: recipe.description,
    url: `${siteUrl}/recipes/${recipe.slug}`,
    image: images.length > 0 ? images : undefined,
    author: { "@type": "Person", name: recipe.author.display_name },
    datePublished: recipe.published_at ? new Date(recipe.published_at).toISOString() : undefined,
    prepTime: isoMinutes(recipe.prep_time_minutes),
    cookTime: isoMinutes(recipe.cook_time_minutes),
    totalTime: isoMinutes(totalMinutes),
    recipeYield: `${recipe.servings} servings`,
    recipeIngredient: recipe.ingredients.map((ingredient) =>
      [ingredient.quantity, ingredient.unit, ingredient.name]
        .filter((part) => part != null && part !== "")
        .join(" "),
    ),
    recipeInstructions: recipe.steps.map((step) => ({
      "@type": "HowToStep",
      name: step.title,
      text: step.description,
    })),
    nutrition: hasNutrition
      ? {
          "@type": "NutritionInformation",
          calories: nutrition.calories != null ? `${nutrition.calories} kcal` : undefined,
          carbohydrateContent:
            nutrition.carbohydrates != null ? `${nutrition.carbohydrates} g` : undefined,
          fatContent: nutrition.fat != null ? `${nutrition.fat} g` : undefined,
          fiberContent: nutrition.fiber != null ? `${nutrition.fiber} g` : undefined,
          proteinContent: nutrition.protein != null ? `${nutrition.protein} g` : undefined,
          sodiumContent: nutrition.sodium != null ? `${nutrition.sodium} mg` : undefined,
        }
      : undefined,
  };
}

/** Serialises JSON-LD for a script tag; `<` is escaped so content cannot close the tag. */
export function serializeJsonLd(data: Record<string, unknown>): string {
  return JSON.stringify(data).replace(/</g, "\\u003c");
}
