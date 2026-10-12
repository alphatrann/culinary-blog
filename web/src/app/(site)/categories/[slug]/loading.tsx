import { RecipeGridSkeleton } from "@/components/recipes/recipe-grid";
import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto max-w-[1200px] px-4 py-10 sm:px-8 sm:py-12">
      <Skeleton className="mb-6 h-5 w-40" />
      <Skeleton className="mb-3 h-11 w-64" />
      <Skeleton className="mb-8 h-5 w-96 max-w-full" />
      <RecipeGridSkeleton count={8} />
    </main>
  );
}
