import { describe, expect, it } from "vitest";
import type { components } from "@/lib/api/schema";
import { buildRecipeJsonLd, buildRecipeMetadata, serializeJsonLd } from "./recipe";

type Recipe = components["schemas"]["RecipeDetailOut"];

const SITE = "https://example.test";

function makeRecipe(overrides: Partial<Recipe> = {}): Recipe {
  return {
    id: "123e4567-e89b-12d3-a456-426614174000",
    slug: "pho-bo",
    title: "Phở bò",
    description: "Nước dùng trong, thơm mùi quế.",
    status: 1,
    published_at: "2026-01-02T03:04:05Z",
    created_at: "2026-01-01T00:00:00Z",
    row_version: 1,
    author_id: "00000000-0000-0000-0000-000000000001",
    author: { id: "00000000-0000-0000-0000-000000000001", display_name: "Lan", avatar_url: null },
    category_id: "00000000-0000-0000-0000-000000000002",
    category: {
      id: "00000000-0000-0000-0000-000000000002",
      name: "Món nước",
      slug: "mon-nuoc",
    } as Recipe["category"],
    difficulty: 2,
    prep_time_minutes: 20,
    cook_time_minutes: 90,
    servings: 4,
    images: [
      {
        id: "img-2",
        original_url: "https://cdn.test/side.jpg",
        is_primary: false,
        order_index: 1,
        alt_text: null,
        medium_url: null,
        thumbnail_url: null,
      },
      {
        id: "img-1",
        original_url: "https://cdn.test/hero.jpg",
        is_primary: true,
        order_index: 0,
        alt_text: null,
        medium_url: null,
        thumbnail_url: null,
      },
    ],
    ingredients: [
      { id: "i1", name: "thịt bò", quantity: 500, unit: "g", notes: null, order_index: 0 },
      { id: "i2", name: "muối", quantity: null, unit: null, notes: null, order_index: 1 },
    ],
    steps: [
      {
        id: "s1",
        step_number: 1,
        title: "Hầm xương",
        description: "Hầm 2 giờ.",
        duration_minutes: 120,
        image_url: null,
      },
    ],
    nutrition: {
      calories: null,
      carbohydrates: null,
      fat: null,
      fiber: null,
      protein: null,
      sodium: null,
    },
    ...overrides,
  } as Recipe;
}

describe("buildRecipeMetadata", () => {
  it("builds the title with the site suffix and absolute canonical", () => {
    const meta = buildRecipeMetadata(makeRecipe(), SITE);
    expect(meta.title).toBe("Phở bò · Culinary Blog");
    expect(meta.alternates?.canonical).toBe("https://example.test/recipes/pho-bo");
    expect(meta.openGraph).toMatchObject({
      title: "Phở bò · Culinary Blog",
      description: "Nước dùng trong, thơm mùi quế.",
      url: "https://example.test/recipes/pho-bo",
      type: "article",
    });
    expect(meta.twitter).toMatchObject({ card: "summary_large_image" });
  });

  it("leaves og and twitter images to the opengraph-image route", () => {
    const meta = buildRecipeMetadata(makeRecipe(), SITE);
    expect(meta.openGraph).not.toHaveProperty("images");
    expect(meta.twitter).not.toHaveProperty("images");
  });

  it("caps the title at 60 characters and keeps the suffix", () => {
    const meta = buildRecipeMetadata(makeRecipe({ title: "A".repeat(100) }), SITE);
    expect(meta.title).toHaveLength(60);
    expect(meta.title).toMatch(/ · Culinary Blog$/);
  });

  it("caps the description at 160 characters", () => {
    const meta = buildRecipeMetadata(makeRecipe({ description: "b".repeat(300) }), SITE);
    expect(meta.description).toHaveLength(160);
  });

  it("marks non-published recipes noindex,nofollow", () => {
    const meta = buildRecipeMetadata(makeRecipe({ status: 2 }), SITE);
    expect(meta.robots).toEqual({ index: false, follow: false });
  });

  it("marks published recipes index,follow", () => {
    const meta = buildRecipeMetadata(makeRecipe(), SITE);
    expect(meta.robots).toEqual({ index: true, follow: true });
  });
});

describe("buildRecipeJsonLd", () => {
  it("emits a Recipe with ISO durations, yield, ingredients and steps", () => {
    const ld = buildRecipeJsonLd(makeRecipe(), SITE);
    expect(ld).toMatchObject({
      "@context": "https://schema.org",
      "@type": "Recipe",
      name: "Phở bò",
      description: "Nước dùng trong, thơm mùi quế.",
      url: "https://example.test/recipes/pho-bo",
      image: ["https://cdn.test/side.jpg", "https://cdn.test/hero.jpg"],
      author: { "@type": "Person", name: "Lan" },
      datePublished: "2026-01-02T03:04:05.000Z",
      prepTime: "PT20M",
      cookTime: "PT90M",
      totalTime: "PT110M",
      recipeYield: "4 servings",
      recipeIngredient: ["500 g thịt bò", "muối"],
      recipeInstructions: [{ "@type": "HowToStep", name: "Hầm xương", text: "Hầm 2 giờ." }],
    });
    expect(ld.nutrition).toBeUndefined();
  });

  it("omits image and datePublished when absent", () => {
    const ld = buildRecipeJsonLd(makeRecipe({ images: [], published_at: null }), SITE);
    expect(ld.image).toBeUndefined();
    expect(ld.datePublished).toBeUndefined();
  });

  it("adds NutritionInformation only when a nutrition field is present", () => {
    const ld = buildRecipeJsonLd(
      makeRecipe({
        nutrition: {
          calories: 350,
          carbohydrates: null,
          fat: null,
          fiber: null,
          protein: 25,
          sodium: null,
        },
      }),
      SITE,
    );
    expect(ld.nutrition).toEqual({
      "@type": "NutritionInformation",
      calories: "350 kcal",
      proteinContent: "25 g",
    });
  });
});

describe("serializeJsonLd", () => {
  it("escapes < so the payload cannot close the script tag", () => {
    const out = serializeJsonLd({ name: "</script><script>alert(1)</script>" });
    expect(out).not.toContain("<");
    expect(JSON.parse(out)).toEqual({ name: "</script><script>alert(1)</script>" });
  });
});
