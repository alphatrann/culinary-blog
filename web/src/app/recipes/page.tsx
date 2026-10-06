import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { RecipeFilterBar } from "@/components/recipes/recipe-filter-bar";
import { RecipeGrid } from "@/components/recipes/recipe-grid";
import { RecipeListError } from "@/components/recipes/recipe-list-error";
import { RecipePagination } from "@/components/recipes/recipe-pagination";
import { serverGet } from "@/lib/api/server";
import {
  buildHref,
  listSortOptions,
  parseListParams,
  type ListSearchParams,
} from "@/lib/list-params";
import { toCardData } from "@/lib/recipes/to-card-data";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Tất cả công thức | Culinary Blog",
  description: "Duyệt, lọc và sắp xếp tất cả công thức nấu ăn của cộng đồng.",
};

const BASE_PATH = "/recipes";

export default async function RecipesPage({
  searchParams,
}: {
  searchParams: Promise<ListSearchParams>;
}) {
  const params = parseListParams(await searchParams);
  const { page, ...filters } = params;
  const hrefParams = { ...filters, sort: filters.sort };

  const [recipesResult, categoriesResult] = await Promise.allSettled([
    serverGet("/recipes", { query: { ...params, page_size: 12 }, revalidate: false }),
    serverGet("/categories", { revalidate: 300 }),
  ]);

  const categories =
    categoriesResult.status === "fulfilled"
      ? categoriesResult.value.map((c) => ({ id: c.id, name: c.name }))
      : undefined;

  const filterBar = (
    <RecipeFilterBar
      basePath={BASE_PATH}
      difficulty={filters.difficulty}
      maxCookTime={filters.max_cook_time}
      sort={filters.sort}
      categoryId={filters.category_id}
      categories={categories}
      sortOptions={listSortOptions}
    />
  );

  let body: React.ReactNode;
  if (recipesResult.status === "rejected") {
    body = (
      <RecipeListError
        error={recipesResult.reason}
        retryHref={buildHref(BASE_PATH, { ...hrefParams, page })}
        clearHref={BASE_PATH}
      />
    );
  } else {
    const list = recipesResult.value;
    if (list.total_pages > 0 && page > list.total_pages) {
      redirect(buildHref(BASE_PATH, { ...hrefParams, page: list.total_pages }));
    }
    body = (
      <>
        <p className="text-muted-foreground" aria-live="polite">
          Hiển thị {list.total_count} công thức
        </p>
        <RecipeGrid
          recipes={list.items.map(toCardData)}
          emptyTitle="Không tìm thấy công thức phù hợp"
          emptyDescription="Hãy thử nới lỏng bộ lọc hoặc xóa bộ lọc để xem tất cả công thức."
          emptyAction={
            <a href={BASE_PATH} className="text-sm font-medium underline">
              Xóa bộ lọc
            </a>
          }
        />
        <RecipePagination
          basePath={BASE_PATH}
          page={list.page}
          totalPages={list.total_pages}
          params={hrefParams}
          className="justify-center"
        />
      </>
    );
  }

  return (
    <main className="mx-auto w-full max-w-[1200px] space-y-6 px-4 py-8 sm:px-8">
      <h1 className="text-page font-bold">Tất cả công thức</h1>
      {filterBar}
      {body}
    </main>
  );
}
