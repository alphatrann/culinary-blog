import { RecipeGridSkeleton } from "@/components/recipes/recipe-grid";
import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto max-w-[1200px] px-4 py-8 min-[768px]:px-8 min-[768px]:py-12">
      <Skeleton className="mb-4 h-6 w-40" />
      <Skeleton className="mb-4 h-12 w-full max-w-lg" />
      <Skeleton className="mb-12 h-11 w-full max-w-[520px]" />
      <RecipeGridSkeleton />
    </main>
  );
}
