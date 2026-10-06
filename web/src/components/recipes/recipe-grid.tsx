import * as React from "react";
import { RecipeCard, type RecipeCardData } from "@/components/recipes/recipe-card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "cn";

const gridClass = "grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4";

function RecipeGrid({
  recipes,
  emptyTitle = "Chưa có công thức nào",
  emptyDescription = "Thử thay đổi bộ lọc hoặc quay lại sau nhé.",
  emptyAction,
  className,
}: {
  recipes: RecipeCardData[];
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: React.ReactNode;
  className?: string;
}) {
  if (recipes.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} action={emptyAction} />;
  }
  return (
    <div className={cn(gridClass, className)}>
      {recipes.map((r) => (
        <RecipeCard key={r.slug} recipe={r} />
      ))}
    </div>
  );
}

/** Use as a `loading.tsx` body or Suspense fallback. */
function RecipeGridSkeleton({ count = 8, className }: { count?: number; className?: string }) {
  return (
    <div role="status" aria-label="Đang tải" className={cn(gridClass, className)}>
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className="overflow-hidden rounded-xl border border-border bg-card">
          <Skeleton className="aspect-[4/3] rounded-none" />
          <div className="space-y-3 p-4">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-1/3" />
          </div>
        </div>
      ))}
    </div>
  );
}

export { RecipeGrid, RecipeGridSkeleton };
