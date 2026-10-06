import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { RecipeGrid } from "@/components/recipes/recipe-grid";
import { Breadcrumb } from "@/components/recipes/detail/breadcrumb";
import { IngredientChecklist } from "@/components/recipes/detail/ingredient-checklist";
import { RecipeGallery } from "@/components/recipes/detail/recipe-gallery";
import { RecipeHeader } from "@/components/recipes/detail/recipe-header";
import { RecipeMeta } from "@/components/recipes/detail/recipe-meta";
import { RecipeNutrition } from "@/components/recipes/detail/recipe-nutrition";
import { RecipeSteps } from "@/components/recipes/detail/recipe-steps";
import { isApiError } from "@/lib/api";
import { serverGet } from "@/lib/api/server";
import { difficultyLabel, formatMinutes } from "@/lib/labels";

export const revalidate = 300;

type Params = Promise<{ slug: string }>;

async function loadRecipe(slug: string) {
  try {
    return await serverGet("/recipes/{slug}", { path: { slug }, revalidate: 300 });
  } catch (e) {
    // 403 = draft/archived seen anonymously; treat like unknown so existence isn't leaked.
    if (isApiError(e) && (e.status === 404 || e.status === 403)) notFound();
    throw e;
  }
}

async function loadRelated(categoryId: string, slug: string) {
  try {
    const list = await serverGet("/recipes", {
      query: { category_id: categoryId, page_size: 4 },
      revalidate: 300,
    });
    return list.items.filter((r) => r.slug !== slug).slice(0, 3);
  } catch {
    return [];
  }
}

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { slug } = await params;
  try {
    const recipe = await serverGet("/recipes/{slug}", { path: { slug }, revalidate: 300 });
    return { title: `${recipe.title} | Culinary Blog`, description: recipe.description };
  } catch {
    return { title: "Không tìm thấy công thức | Culinary Blog" };
  }
}

export default async function RecipePage({ params }: { params: Params }) {
  const { slug } = await params;
  const recipe = await loadRecipe(slug);
  const related = await loadRelated(recipe.category_id, recipe.slug);

  return (
    <main className="mx-auto w-full max-w-[1200px] px-4 sm:px-8">
      <Breadcrumb
        items={[
          { label: "Trang chủ", href: "/" },
          { label: recipe.category.name, href: `/recipes?category=${recipe.category.slug}` },
          { label: recipe.title },
        ]}
      />
      <article>
        <RecipeHeader
          title={recipe.title}
          description={recipe.description}
          category={recipe.category}
          authorName={recipe.author.display_name}
          publishedAt={recipe.published_at}
        />
        <RecipeGallery images={recipe.images} title={recipe.title} slug={recipe.slug} />
        <RecipeMeta
          prepMinutes={recipe.prep_time_minutes}
          cookMinutes={recipe.cook_time_minutes}
          servings={recipe.servings}
          difficulty={recipe.difficulty}
        />
        <div className="mt-10 grid items-start gap-10 lg:mt-12 lg:grid-cols-[minmax(0,380px)_minmax(0,1fr)] lg:gap-14">
          <IngredientChecklist ingredients={recipe.ingredients} />
          <RecipeSteps steps={recipe.steps} />
        </div>
        <RecipeNutrition nutrition={recipe.nutrition} />
      </article>
      {related.length > 0 && (
        <section
          aria-labelledby="related-heading"
          className="mt-12 pb-10 sm:mt-16 sm:pb-16 print:hidden"
        >
          <h2 id="related-heading" className="mb-5 text-2xl font-semibold sm:text-section">
            Công thức cùng danh mục
          </h2>
          <RecipeGrid
            recipes={related.map((r) => ({
              slug: r.slug,
              title: r.title,
              category: r.category_name,
              thumbnailUrl: r.thumbnail_url,
              time: formatMinutes(r.prep_time_minutes + r.cook_time_minutes),
              difficulty: difficultyLabel(r.difficulty),
              author: r.author_name,
            }))}
          />
        </section>
      )}
    </main>
  );
}
