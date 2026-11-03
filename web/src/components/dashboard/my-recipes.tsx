"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { Pagination } from "@/components/ui/pagination";
import { Skeleton } from "@/components/ui/skeleton";
import { api, type ResponseBody } from "@/lib/api";
import { recipeStatusLabel } from "@/lib/labels";
import { PUBLISHED_STATUS } from "@/lib/recipes/edit";
import {
  MY_RECIPE_TABS,
  MY_RECIPES_PAGE_SIZE,
  myRecipesHref,
  type MyRecipeTab,
  tabStatusFilter,
} from "@/lib/recipes/my-recipes";
import { cn } from "cn";

export type RecipeSummary = ResponseBody<"/recipes", "get">["items"][number];

const TAB_LABELS: Record<MyRecipeTab, string> = {
  all: "Tất cả",
  published: "Đã xuất bản",
  draft: "Bản nháp",
  archived: "Đã lưu trữ",
};

const dateFormat = new Intl.DateTimeFormat("vi-VN", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

export function formatUpdated(iso: string | null): string {
  return iso ? dateFormat.format(new Date(iso)) : "—";
}

/** One recipe as a row: title, category, updated date, status, and the edit (and view, once published) links. */
export function RecipeRows({ items }: { items: RecipeSummary[] }) {
  return (
    <ul className="divide-y divide-border rounded-xl border border-border bg-card">
      {items.map((recipe) => (
        <li key={recipe.id} className="flex flex-wrap items-center gap-3 px-4 py-4 sm:px-6">
          <div className="min-w-0 flex-1">
            <Link
              href={`/dashboard/recipes/${recipe.id}/edit`}
              className="block truncate font-heading text-lg font-semibold hover:underline"
            >
              {recipe.title}
            </Link>
            <p className="text-[13px] text-muted-foreground">
              {recipe.category_name}
              {recipe.updated_at && ` · Cập nhật ${formatUpdated(recipe.updated_at)}`}
            </p>
          </div>
          <Badge variant={recipe.status === PUBLISHED_STATUS ? "count" : "outline"}>
            {recipeStatusLabel(recipe.status)}
          </Badge>
          <div className="flex gap-2">
            <Link
              href={`/dashboard/recipes/${recipe.id}/edit`}
              className="text-sm font-medium text-primary hover:underline"
            >
              Sửa
            </Link>
            {recipe.status === PUBLISHED_STATUS && (
              <Link
                href={`/recipes/${recipe.slug}`}
                className="text-sm text-muted-foreground hover:underline"
              >
                Xem
              </Link>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}

/** The author's recipes with status tabs. Used by the dashboard list page and the profile. */
export function MyRecipes({
  basePath,
  tab,
  page,
}: {
  basePath: string;
  tab: MyRecipeTab;
  page: number;
}) {
  const query = useQuery({
    queryKey: ["my-recipes", tab, page],
    queryFn: () =>
      api.get("/recipes", {
        query: {
          author_id: "me",
          status: tabStatusFilter(tab),
          page,
          page_size: MY_RECIPES_PAGE_SIZE,
        },
      }),
  });

  return (
    <section className="flex flex-col gap-5" aria-label="Danh sách công thức">
      <Tabs basePath={basePath} active={tab} counts={query.data?.status_counts ?? null} />
      {query.isPending && <Skeleton className="h-48 w-full" aria-label="Đang tải công thức" />}
      {query.isError && (
        <EmptyState
          title="Không tải được công thức"
          description="Vui lòng tải lại trang sau ít phút."
        />
      )}
      {query.data && query.data.items.length === 0 && (
        <EmptyState
          title={tab === "all" ? "Bạn chưa có công thức nào" : "Không có công thức trong mục này"}
          description="Chia sẻ món ăn của bạn với mọi người."
          action={
            <Link
              href="/dashboard/recipes/new"
              className="font-medium text-primary hover:underline"
            >
              Viết công thức mới
            </Link>
          }
        />
      )}
      {query.data && query.data.items.length > 0 && (
        <>
          <RecipeRows items={query.data.items} />
          <Pagination
            page={page}
            pageCount={query.data.total_pages}
            hrefFor={(p) => myRecipesHref(basePath, tab, p)}
          />
        </>
      )}
    </section>
  );
}

function Tabs({
  basePath,
  active,
  counts,
}: {
  basePath: string;
  active: MyRecipeTab;
  counts: { draft: number; published: number; archived: number } | null;
}) {
  const count = (t: MyRecipeTab) => {
    if (!counts) return null;
    if (t === "all") return counts.draft + counts.published + counts.archived;
    return counts[t];
  };
  return (
    <nav aria-label="Lọc theo trạng thái" className="flex flex-wrap gap-2">
      {MY_RECIPE_TABS.map((t) => {
        const isActive = t === active;
        const n = count(t);
        return (
          <Link
            key={t}
            href={myRecipesHref(basePath, t, 1)}
            aria-current={isActive ? "page" : undefined}
            className={cn(
              "inline-flex min-h-11 items-center gap-2 rounded-full border px-4 text-sm font-medium",
              isActive
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border bg-card hover:bg-accent",
            )}
          >
            {TAB_LABELS[t]}
            {n !== null && <span className="tabular-nums opacity-80">{n}</span>}
          </Link>
        );
      })}
    </nav>
  );
}
