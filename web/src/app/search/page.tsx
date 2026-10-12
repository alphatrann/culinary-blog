import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Search } from "lucide-react";
import { RecipeGrid } from "@/components/recipes/recipe-grid";
import { RecipeListError } from "@/components/recipes/recipe-list-error";
import { RecipePagination } from "@/components/recipes/recipe-pagination";
import { ActiveFilterChips } from "@/components/search/active-filter-chips";
import { SearchFilterPanel } from "@/components/search/search-filter-panel";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { serverGet } from "@/lib/api/server";
import {
  buildHref,
  parseListParams,
  parseSearchQuery,
  type ListSearchParams,
} from "@/lib/list-params";
import { toCardData } from "@/lib/recipes/to-card-data";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Tìm kiếm công thức | Culinary Blog",
  description: "Tìm công thức nấu ăn theo tên món.",
};

const BASE_PATH = "/search";

function SearchBox({ q }: { q: string }) {
  return (
    <form role="search" action={BASE_PATH} method="get" className="flex max-w-[560px] gap-2">
      <label htmlFor="search-page-q" className="sr-only">
        Tìm công thức
      </label>
      <Input
        id="search-page-q"
        name="q"
        type="search"
        defaultValue={q}
        placeholder="Tìm công thức"
        className="flex-1"
      />
      <Button type="submit">
        <Search aria-hidden="true" className="size-4" />
        Tìm kiếm
      </Button>
    </form>
  );
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<ListSearchParams>;
}) {
  const sp = await searchParams;
  const query = parseSearchQuery(sp);
  const { page, ...filters } = parseListParams(sp);
  // The search endpoint is relevance-only; `sort` is not part of this page.
  const { sort: _sort, ...searchFilters } = filters;
  void _sort;

  if (query.state !== "valid") {
    return (
      <main className="mx-auto w-full max-w-[1200px] space-y-6 px-4 py-8 sm:px-8">
        <h1 className="text-page font-bold">
          {query.state === "empty" ? "Hôm nay bạn muốn nấu món gì?" : "Tìm kiếm công thức"}
        </h1>
        <SearchBox q={query.q} />
        <p
          className="text-muted-foreground"
          role={query.state === "too_short" ? "alert" : undefined}
        >
          {query.state === "empty"
            ? "Nhập tên món ăn để bắt đầu tìm."
            : "Nhập ít nhất 2 ký tự để tìm kiếm nhé."}
        </p>
      </main>
    );
  }

  const { q } = query;
  const hrefParams = { q, ...searchFilters };

  const [resultsResult, categoriesResult] = await Promise.allSettled([
    serverGet("/recipes/search", {
      query: { q, page, ...searchFilters, page_size: 12 },
      revalidate: false,
    }),
    serverGet("/categories", { revalidate: 300 }),
  ]);

  const categories =
    categoriesResult.status === "fulfilled"
      ? categoriesResult.value.map((c) => ({ id: c.id, name: c.name }))
      : undefined;

  let body: React.ReactNode;
  if (resultsResult.status === "rejected") {
    body = (
      <RecipeListError
        error={resultsResult.reason}
        retryHref={buildHref(BASE_PATH, { ...hrefParams, page })}
        clearHref={buildHref(BASE_PATH, { q })}
      />
    );
  } else {
    const results = resultsResult.value;
    if (results.total_pages > 0 && page > results.total_pages) {
      redirect(buildHref(BASE_PATH, { ...hrefParams, page: results.total_pages }));
    }
    body = (
      <>
        <p className="text-muted-foreground" aria-live="polite">
          Tìm thấy {results.total_count} công thức
        </p>
        <ActiveFilterChips
          basePath={BASE_PATH}
          q={q}
          filters={searchFilters}
          categories={categories}
        />
        <RecipeGrid
          recipes={results.items.map(toCardData)}
          emptyTitle={`Chưa tìm thấy công thức nào cho “${q}”`}
          emptyDescription="Thử gõ từ khóa ngắn hơn hoặc bỏ bớt bộ lọc."
          emptyAction={
            <a href={buildHref(BASE_PATH, { q })} className="text-sm font-medium underline">
              Xóa bộ lọc
            </a>
          }
        />
        <RecipePagination
          basePath={BASE_PATH}
          page={results.page}
          totalPages={results.total_pages}
          params={hrefParams}
          className="justify-center"
        />
      </>
    );
  }

  return (
    <main className="mx-auto w-full max-w-[1200px] space-y-6 px-4 py-8 sm:px-8">
      <h1 className="text-page font-bold">Kết quả cho “{q}”</h1>
      <SearchBox q={q} />
      <div className="grid gap-6 border-t border-border pt-6 min-[1000px]:grid-cols-[280px_1fr]">
        <SearchFilterPanel
          basePath={BASE_PATH}
          q={q}
          categories={categories}
          categoryId={searchFilters.category_id}
          difficulty={searchFilters.difficulty}
          maxCookTime={searchFilters.max_cook_time}
        />
        <div className="min-w-0 space-y-6">{body}</div>
      </div>
    </main>
  );
}
