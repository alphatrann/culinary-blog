import type { Metadata } from "next";
import Link from "next/link";
import { CategoryChips } from "@/components/home/category-chips";
import { Hero } from "@/components/home/hero";
import { RecipeFilterBar } from "@/components/recipes/recipe-filter-bar";
import { RecipeGrid } from "@/components/recipes/recipe-grid";
import { RecipePagination } from "@/components/recipes/recipe-pagination";
import { toRecipeCardData } from "@/components/recipes/recipe-card-data";
import { Alert } from "@/components/ui/alert";
import { serverGet } from "@/lib/api/server";

export const revalidate = 3600;

export const metadata: Metadata = {
  title: { absolute: "Culinary Blog – Công thức nấu ăn Việt" },
  description:
    "Công thức nấu ăn Việt từng bước, nguyên liệu rõ ràng. Tìm món bạn muốn nấu hôm nay.",
};

const PAGE_SIZE = 8;

async function loadHome() {
  try {
    const [recipes, categories] = await Promise.all([
      serverGet("/recipes", { query: { page: 1, page_size: PAGE_SIZE }, revalidate }),
      serverGet("/categories", { revalidate }),
    ]);
    return { recipes, categories };
  } catch {
    return null;
  }
}

export default async function Home() {
  const data = await loadHome();
  // Featured = newest published recipe; the API has no featured flag (#36).
  const newest = data?.recipes.items[0];

  return (
    <main>
      <Hero
        featured={
          newest && {
            slug: newest.slug,
            title: newest.title,
            description: newest.description,
            thumbnailUrl: newest.thumbnail_url,
          }
        }
      />
      <section className="border-t border-border pt-6 min-[768px]:pt-10">
        <div className="mx-auto max-w-[1200px] px-4 min-[768px]:px-8">
          {!data ? (
            <Alert>
              Không thể tải công thức lúc này. Vui lòng thử lại sau hoặc{" "}
              <Link href="/recipes" className="underline">
                xem tất cả công thức
              </Link>
              .
            </Alert>
          ) : (
            <>
              <CategoryChips categories={data.categories} />
              <div className="mt-7 mb-5 flex flex-wrap items-end justify-between gap-5 min-[768px]:mt-10 min-[768px]:mb-6">
                <div>
                  <h2 className="mb-1 text-2xl leading-[1.15] font-bold min-[768px]:text-section">
                    Công thức mới nhất
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    {data.recipes.total_count > data.recipes.items.length
                      ? `Hiển thị ${data.recipes.items.length} trên ${data.recipes.total_count} công thức`
                      : `Hiển thị ${data.recipes.items.length} công thức`}
                  </p>
                </div>
                <RecipeFilterBar basePath="/recipes" />
              </div>
              <RecipeGrid recipes={data.recipes.items.map(toRecipeCardData)} />
              <RecipePagination
                basePath="/recipes"
                page={data.recipes.page}
                totalPages={data.recipes.total_pages}
                className="mt-8 pb-10 min-[768px]:mt-12 min-[768px]:pb-16"
              />
            </>
          )}
        </div>
      </section>
    </main>
  );
}
