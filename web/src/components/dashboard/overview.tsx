"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { useUser } from "@/lib/session";
import { RecipeRows } from "./my-recipes";

const RECENT_COUNT = 5;

/** Status totals and the most recently updated recipes for the signed-in author. */
export function DashboardOverview() {
  const { user } = useUser();
  const query = useQuery({
    queryKey: ["my-recipes", "overview"],
    queryFn: () => api.get("/recipes", { query: { author_id: "me", page_size: RECENT_COUNT } }),
  });

  if (query.isPending) return <Skeleton className="h-64 w-full" aria-label="Đang tải tổng quan" />;
  if (query.isError) {
    return (
      <EmptyState
        title="Không tải được tổng quan"
        description="Vui lòng tải lại trang sau ít phút."
      />
    );
  }

  const counts = query.data.status_counts ?? { draft: 0, published: 0, archived: 0 };
  const stats = [
    { label: "Đã xuất bản", value: counts.published },
    { label: "Bản nháp", value: counts.draft },
    { label: "Tổng cộng", value: counts.draft + counts.published + counts.archived },
  ];

  return (
    <div className="flex flex-col gap-8">
      {user && <p className="text-lg text-muted-foreground">Xin chào, {user.display_name}.</p>}
      <dl className="grid grid-cols-3 gap-3">
        {stats.map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-border bg-card p-4 text-center sm:p-6"
          >
            <dt className="text-[13px] text-muted-foreground">{s.label}</dt>
            <dd className="font-heading text-3xl font-semibold tabular-nums">{s.value}</dd>
          </div>
        ))}
      </dl>
      <section aria-labelledby="recent-heading" className="flex flex-col gap-4">
        <div className="flex items-baseline justify-between gap-4">
          <h2 id="recent-heading" className="font-heading text-2xl font-semibold">
            Công thức gần đây
          </h2>
          <Link
            href="/dashboard/recipes"
            className="text-sm font-medium text-primary hover:underline"
          >
            Xem tất cả
          </Link>
        </div>
        {query.data.items.length === 0 ? (
          <EmptyState
            title="Bạn chưa có công thức nào"
            description="Bắt đầu với một món bạn thường nấu."
            action={
              <Link
                href="/dashboard/recipes/new"
                className="font-medium text-primary hover:underline"
              >
                Viết công thức mới
              </Link>
            }
          />
        ) : (
          <RecipeRows items={query.data.items} />
        )}
      </section>
    </div>
  );
}
