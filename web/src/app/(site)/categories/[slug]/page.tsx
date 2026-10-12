import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { RecipeGrid } from "@/components/recipes/recipe-grid";
import { RecipePagination } from "@/components/recipes/recipe-pagination";
import { serverGet } from "@/lib/api/server";
import { isApiError } from "@/lib/api";
import { difficultyLabel, formatMinutes } from "@/lib/labels";
import { parseListParams, type ListSearchParams } from "@/lib/list-params";

export const revalidate = 600;

const PAGE_SIZE = 12;

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<ListSearchParams>;
};

async function loadCategory(slug: string, page: number) {
  try {
    return await serverGet("/categories/{slug}", {
      path: { slug },
      query: { page, page_size: PAGE_SIZE },
      revalidate: 600,
    });
  } catch (error) {
    if (isApiError(error) && error.status === 404) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const { category } = await loadCategory(slug, 1);
  return {
    title: `${category.name} | Culinary Blog`,
    description: category.description ?? `Công thức nấu ăn thuộc danh mục ${category.name}.`,
  };
}

export default async function CategoryPage({ params, searchParams }: Props) {
  const { slug } = await params;
  const { page } = parseListParams(await searchParams);
  const { category, recipes } = await loadCategory(slug, page);

  return (
    <main className="mx-auto max-w-[1200px] px-4 py-10 sm:px-8 sm:py-12">
      <nav aria-label="Đường dẫn" className="mb-6 text-muted-foreground">
        <ol className="flex flex-wrap items-center gap-2">
          <li>
            <Link href="/categories" className="hover:text-foreground hover:underline">
              Danh mục
            </Link>
          </li>
          <li aria-hidden>›</li>
          <li aria-current="page" className="text-foreground">
            {category.name}
          </li>
        </ol>
      </nav>
      <header className="mb-8 max-w-2xl">
        <h1 className="mb-3 text-page font-bold">{category.name}</h1>
        {category.description && (
          <p className="mb-3 text-lede text-pretty text-muted-foreground">{category.description}</p>
        )}
        <p className="text-sm font-semibold text-muted-foreground">
          {category.recipe_count} công thức
        </p>
      </header>
      <RecipeGrid
        emptyTitle="Danh mục này chưa có công thức"
        emptyDescription="Hãy quay lại sau hoặc xem các danh mục khác."
        emptyAction={
          <Link
            href="/categories"
            className="font-medium text-herb underline-offset-4 hover:underline"
          >
            Xem tất cả danh mục
          </Link>
        }
        recipes={recipes.items.map((r) => ({
          slug: r.slug,
          title: r.title,
          category: r.category_name,
          thumbnailUrl: r.thumbnail_url,
          time: formatMinutes(r.prep_time_minutes + r.cook_time_minutes),
          difficulty: difficultyLabel(r.difficulty as number),
          author: r.author_name,
        }))}
      />
      <RecipePagination
        basePath={`/categories/${slug}`}
        page={recipes.page}
        totalPages={recipes.total_pages}
        className="mt-10"
      />
    </main>
  );
}
