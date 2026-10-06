import { CategoryGridSkeleton } from "@/components/categories/category-card";
import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto max-w-[1200px] px-4 py-10 sm:px-8 sm:py-12">
      <Skeleton className="mb-8 h-11 w-48" />
      <CategoryGridSkeleton />
    </main>
  );
}
