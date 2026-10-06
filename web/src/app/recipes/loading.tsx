import { RecipeGridSkeleton } from "@/components/recipes/recipe-grid";

export default function Loading() {
  return (
    <main className="mx-auto w-full max-w-[1200px] space-y-6 px-4 py-8 sm:px-8">
      <h1 className="text-page font-bold">Tất cả công thức</h1>
      <RecipeGridSkeleton count={12} />
    </main>
  );
}
